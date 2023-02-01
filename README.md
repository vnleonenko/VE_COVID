# VE_COVID

1. Необходимо создать виртуальное окружение для проекта, куда будут установлены все зависимости.

    ```python3 -m pip install --user virtualenv``` - устанавливает пакет для создания виртуального окружения

    ```python3 -m venv myenv``` - создает окружение в той директории, откуда вызывается

    ```source env/bin/activate``` - активируем окружение.

    Для проверки работоспособности созданного окружения достаточно убедиться, что используется интерпретатор окружения
```which python``` 

2. Для установки необходимых зависимостей необходимо исполнить команду

    ```python3 -m pip install -r requirements.txt```

3. Запуск расчета ЭВ осуществляется из консоли с помощью файла main.py в директории 
calculations/src. В модуле совмещены функции расчета оценок ЭВ, а также выгрузки
сгенерированного файла в базу данных. Чтобы начать расчет для точек, записанных в файл
data_points.txt, и субъектов в файле subjects.txt для 3х возрастных групп, команда,
вводимая в консоль, выглядит как:

    ```python main.py compute_ve --age_groups 3 --data_points ./input/data_points.txt --subjects ./input/subjects.txt```
    
    Для расчета ЭВ с дифференциацией по возрастным группам и периодам после вакцинации:

    ```python main.py compute_ve --age_groups 9 --vac_intervals --data_points ./input/data_points.txt --subjects ./input/subjects.txt```

    Все аргументы являются обязательными, кроме ```vac_intervals```, это значение по умолчанию False, но при наличии этого 
аргумента значение меняется на True и расчет происходит с учетом разбивки на периоды после вакцинации.
4. Для выгрузки рассчитанных данных в бд необходимо выполнить команду:
   
   ```python main.py unload_ve --file_path path/to/file.csv```
   Аргумент ```--file_path``` также является обязательным.
