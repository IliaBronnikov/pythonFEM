#### Интерфейc программы
При запуска вам будет предложено ввести два параметра:
- Коэффициент Лама
- Коэффициент Мю

![alt text](screenshots/interface.PNG?raw=true)

После ввода необходимо нажать "Вычислить", после чего будет выведено поле деформаций

![alt text](screenshots/deformation_field.PNG?raw=true)

При нажатии кнопки "print view", выводится деформируемое состояние

![alt text](screenshots/deformation_view.PNG?raw=true)

Результат можно записать в БД с помощью кнопки "Записать в БазуДанных", сохраненные результаты в БД выводится при каждом запуске







#### Установка проекта

- установить версию python 3.7
- создать виртуальное окружение 
```shell script
python3.7 -m venv venv
```
- активировать виртуальное окружение
```shell script
source venv/bin/activate
```
- установить зависимости
```shell script
pip install -r requirements.txt
```
- запустить файл
```shell script
fem_solver_sfepy.py
