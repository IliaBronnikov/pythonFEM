from tkinter import *
import numpy as nm
import sqlite3
from vtk import *

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# =======================create datebase====================================
# cursor.execute("""CREATE TABLE albums
#                   (parametr_lame real,parametr_mu real,max_disp real)
#                 """)

# =======================input datebase====================================
# cursor.execute("""INSERT INTO albums
#                   VALUES ('', '')
#                     """)
# conn.commit()


# =======================output datebase====================================

# sql = "SELECT  FROM albums WHERE parametr_value = ?"
# cursor.execute(sql, [*])
# print(cursor.fetchall())

# =======================output datebase====================================
for row in cursor.execute("SELECT rowid, * FROM albums ORDER BY parametr_lame"):
    print(row)

root =Tk()
root.title("Вычисление перемещений")
# l = Label(text = "Введите коэф.Ламе", fg='black', width=50).grid(row = 0, column = 0)
Label(text = "Введите коэф.Ламе", fg='black', width = 20).grid(row = 0, column = 0)
Label(text = "Введите коэф.Мю", fg='black', width = 20).grid(row = 0, column = 2)

e_lame = Entry(width = 20)
e_lame.grid(row = 1, column = 0)
e_mu = Entry (width = 20)
e_mu.grid(row = 1, column = 2)
b = Button(text="Вычислить")
b.grid(row = 3, column = 1)
b_db = Button(text="Записать в БазуДанных")
b_db.grid(row = 4,column = 1)
displacement = 0.0


def result(event):
    # glodal displacement
    if not e_lame.get().isdigit() or not e_mu.get().isdigit():
        if not e_lame.get().isdigit():
            e_lame.delete(0, END)
            e_lame.insert(0,"wrong value")
        if not e_mu.get().isdigit():
            e_mu.delete(0, END)
            e_mu.insert(0,"wrong value")
    else:
        coef_lame = e_lame.get()
        coef_lame = float(coef_lame)
        coef_mu = e_mu.get()
        coef_mu = float(coef_mu)

        global displacement
        from sfepy.discrete.fem import Mesh, FEDomain, Field


        # =====================load mesh====================================

        # mesh = Mesh.from_file('rectangle_tri.mesh')
        mesh = Mesh.from_file('square_1m.mesh')


        # =====================createa domain on mesh====================================

        domain = FEDomain('domain', mesh)
        min_x, max_x = domain.get_mesh_bounding_box()[:,0]
        eps = 1e-8 * (max_x - min_x)
        omega = domain.create_region('Omega', 'all')
        gamma1 = domain.create_region('Gamma1', 'vertices in x < %.10f' % (min_x + eps), 'facet')
        gamma2 = domain.create_region('Gamma2', 'vertices in x > %.10f' % (max_x - eps), 'facet')

        field = Field.from_args('fu', nm.float64, 'vector', omega, approx_order = 2)

        from sfepy.discrete import (FieldVariable, Material, Integral, Function, Equation, Equations, Problem)

        u = FieldVariable('u', 'unknown', field)
        v = FieldVariable('v', 'test', field, primary_var_name = 'u')

        from sfepy.mechanics.matcoefs import stiffness_from_lame
        m = Material('m', D=stiffness_from_lame(dim=2, lam=coef_lame, mu=coef_mu))
        # f = Material('f', val=[[0.02], [0.01]])
        f = Material('f', val=[[1.0], [0.0]])

        integral = Integral('i', order=3)

        from sfepy.terms import Term
        t1 = Term.new('dw_lin_elastic(m.D, v, u)', integral, omega, m=m, v=v, u=u)  #for boundary cond displacement
        t2 = Term.new('dw_volume_lvf(f.val, v)', integral, omega, f=f, v=v)   #for boundary cond force
        eq = Equation('balance', t1+t2)
        eqs = Equations([eq])

        from sfepy.discrete.conditions import Conditions, EssentialBC
        fix_u = EssentialBC('fix_u', gamma1, {'u.all' : 0.0}) #ставим ГУ на границу гамма 1, перемещения 0
        # fix_u2 = EssentialBC('fix_u', gamma2, {'u.[1]': 0.0}) #ставим ГУ на границу гамма 2, перемещения по оси Y 0
        # shift_u = EssentialBC('shift_u', gamma2, {'u.[0]': 0}) #ставим ГУ на границу гамма 2, перемещения по оси Х 0

        from sfepy.base.base import IndexedStruct
        from sfepy.solvers.ls import ScipyDirect
        from sfepy.solvers.nls import Newton

        ls = ScipyDirect({})
        nls_status = IndexedStruct()
        nls = Newton({}, lin_solver=ls, status=nls_status)

        pb = Problem('elasticity', equations = eqs)

        pb.save_regions_as_groups('regions')


        # =====================постпроцессинг====================================
        from sfepy.postprocess.viewer import Viewer
        # view = Viewer('regions.vtk')
        # # view()


        pb.set_bcs(ebcs=Conditions([fix_u]))#, shift_u,fix_u2])) #прикладываем ГУ
        pb.set_solver(nls)

        status = IndexedStruct()
        vec = pb.solve(status=status)

        print('Nonlinear solver status:\n', nls_status)
        print('Stationary solver status:\n', status)

        # =====================векторы перемещения====================================
        pb.save_state('linear_elasticity.vtk', vec)
        view = Viewer('linear_elasticity.vtk')
        view()

        # =====================отображение перемещений====================================
        view(vector_mode='warp_norm', rel_scaling=1, is_scalar_bar=True, is_wireframe=True)

        # =====================выгрузка перемещений====================================
        output_dict = vec.create_output_dict(fill_value=None,
                                             extend=True,
                                             linearization=None)
        displacement = max(abs(output_dict['u'].data[:,0]))
        return displacement

def db(event):
    global displacement
    coef_lame = e_lame.get()
    coef_mu = e_mu.get()
    values = [(float(coef_lame),float(coef_mu),round(displacement,3))]
    cursor.executemany("INSERT INTO albums VALUES (?,?,?)", values)
    print("write_to_db")
    conn.commit()
    e_lame.delete(0, END)
    e_mu.delete(0, END)

b_db.bind('<Button-1>', db)
b.bind('<Button-1>', result)

root.mainloop()