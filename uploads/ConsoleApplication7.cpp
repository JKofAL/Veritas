#include <iostream>
using namespace std;

void task1() {
    int w;
    cout << "Длина массива: ";
    cin >> w;
    int* arr = new int[w];
    for (int i = 0; i < w; ++i) {
        int q;
        cout << "Введите элемент массива(" << i + 1 << ")";
        cin >> q;
        arr[i] = q;
    }
    for (int i = 0; i < w; ++i) {
        cout << arr[i];
    }
    delete[] arr;
}

void task2() {
    int q;
    cout << "Введите длину массива: ";
    cin >> q;
    int* arr = new int[q];
    int sum = 0;
    for (int i = 0; i < q; ++i) {
        int w;
        cout << "\nВведите " << i + 1 << " элемент массива: ";
        cin >> w;
        sum += w;
    }
    cout << "Суииа всех элементов массива = " << sum;
    delete[] arr;
}

void task3() {
    int rows;
    int cols;
    cout << "Введите колличестыо строк: ";
    cin >> rows;
    cout << "\n" << "Введите колличество столбцов: ";
    cin >> cols;
    int** arr = new int* [rows];
    for (int i = 0; i < rows; ++i) {
        arr[i] = new int[cols];
    }

    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            int q;
            cout << "Введите элемент, который будет находиться в " << i + 1 << " строке в " << j + 1 << " столбце: ";
            cin >> q;
            arr[i][j] = q;
        }
    }

    cout << "Исходная матрица" << "\n";
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            cout << arr[i][j] << "\t";
        }
        cout << "\n";
    }
    cout << "Транспонированная матрица" << "\n";
    int** trarr = new int* [cols];
    for (int i = 0; i < cols; ++i) {
        trarr[i] = new int[rows];
    }

    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            trarr[j][i] = arr[i][j];
        }
    }
    for (int i = 0; i < cols; ++i) {
        for (int j = 0; j < rows; ++j) {
            cout << trarr[i][j] << '\t';
        }
        cout << '\n';
    }

    for (int i = 0; i < rows; ++i) {
        delete[] trarr[i];
    }

    delete[] trarr;

    for (int i = 0; i < rows; ++i) {
        delete[] arr[i];
    }
    delete[] arr;
}

void task4() {
    int q;
    cout << "Введите систему координат(вектора а): ";
    cin >> q;
    int* vectora = new int[q];
    int w;
    cout << "Введите систему координат(вектора b): ";
    cin >> w;
    int* vectorb = new int[w];
    if (q == 2 && w == 2) {
        for (int i = 0; i < q; ++i) {
            int q;
            cin >> q;
            vectora[i] = q;
        }
        for (int i = 0; i < w; ++i) {
            int q;
            cin >> q;
            vectorb[i] = q;
        }
        int res = 0;
        for (int i = 0; i < q; ++i) {
            res += vectora[i] * vectorb[i];
        }
        cout << "Скалярное произведение: " << res << '\n';
    }
    if (q == 3 && w == 3) {
        for (int i = 0; i < q; ++i) {
            int q;
            cin >> q;
            vectora[i] = q;
        }
        for (int i = 0; i < w; ++i) {
            int q;
            cin >> q;
            vectorb[i] = q;
        }
        int res = 0;
        for (int i = 0; i < q; ++i) {
            res += vectora[i] * vectorb[i];
        }
        cout << "Скалярное произведение: " << res << '\n';
    }
    delete[] vectorb;
    delete[] vectora;
}


void menu() {
    int a;
    cout << "1. Написать программу, которая выводит на экран элементы одномерного массива с использованием указателей." << "\n" << "2. Разработать программу для нахождения суммы элементов одномерного массива с помощью указателей." << '\n' << "3. Создать программу, которая транспонирует двумерный массив (матрицу) с использованием указателей." << '\n' << "4. Написать программу, которая находит скалярное произведение двух векторов, представленных в виде одномерных массивов и обрабатываемых через указатели." << '\n' << "Введите номер задания: ";
    cin >> a;
    switch (a) {
    case 1:
        task1();
        break;
    case 2:
        task2();
        break;
    case 3:
        task3();
        break;
    case 4:
        task4();
        break;
    }

}

int main()
{
    setlocale(LC_ALL, "ru");
    menu();
}







