Arithmetic Operators（数学运算符）


Common Python math Operators/functions
+ - * // ** % /



Operator	Meaning	Example
+	Addition(加法)	3 + 2
-	Subtraction(减法)	6 - 1
*	Multiplication(乘法)	3 * 4
/	Division(除法)	4 / 2
//	Integer Division(商)	4 // 2
**	Power(乘方)	2 ** 3
%	Remainder(余数)	6 % 5







计算机的储存模式


 


Integer（整数）
Question：
计算机是怎么储存整数的？

二进制	十进制	二进制	十进制
0000	0	0101	5
0001	1	0110	6
0010	2	0111	7
0011	3	1000	8
0100	4	1001	9



Example:
如何将1010 转为十进制数？

 

Exercise:
	1001 1101 转换为10进制是多少




	最大的8位2进制数是多少？






Float

Question：
计算机又是怎么储存小数的？


Example
把 〖101.1101〗_2 转化为小数

 



Note:
	计算机无法记录无限小数，比如 1/3 ，对于64位浮点数来说，尾数的上限是51位。
	如果尾数超过51位，那么多余的部分将会被截掉，因此计算机表示的许多小数会有误差，这种误差我们叫做（round-off error）。
	在python中，最大的数是float（‘inf’），最小的数是float（‘-inf’）


同学们可以发现，在计算机中，小数的存储方式和整数的存储方式有非常大的区别，因此，在计算机中的计算，我们需要care计算结果的数据类型是什么




总结
对于除法（/）操作符来说：它的结果一定为小数（float number）。
2 / 3 = 1.5
6 / 2 = 3.0
6.0 / 2 = 3.0

对于其他操作符来说（加法（+），减法（-），乘法（*），整数除法（//），乘方（**），余数（%））如果操作符的任意一边为小数，则结果为小数（float number）。如果操作符的两边都为整数(Integer)，那么结果为整数(Integer)。


Note：
任何数除以0会得到ZeroDivisionError



Question：

请问如下哪个是对的？
3^(3^2 )=3^9=19683
3^(3^2 )=27^2=729 



请问如下的计算结果是什么？
6÷2(1+2)




操作符的运算顺序：
	括号拥有最高的优先级，比如(2 + 3) * 4, 这个式子会先被运算为5 * 4
	**
	*，/ , % 
	+, -
同时出现的话，最左的优先级最高


在计算机中，下列运算的结果是什么？

8 / 2 *(2+2)



6 / 3 * 2+1



6 / 3 *(2+1)



(3 / 1000) * 2 + 2 ** 3 * 1



(3.0 // 1000) *  2 + 2 ** 3 * 1





Common Math Functions

Common Python math functions
min, max, round, abs, int, float, …


Min/Max
min(3, 1, 4)          # 输出：1
min([5, -2, 7, 0])    # 输出：-2
max(3, 1, 4)          # 输出：4
max([5, -2, 7, 0])    # 输出：7

Round
round(3.14159)        # 输出：3
round(3.14159, 2)     # 输出：3.14
round(2.5)            # 输出：2
round(3.5)            # 输出：4

abs
abs(-5)               # 输出：5
abs(3.7)              # 输出：3.7

int/float
int(3.9)              # 输出：3
int(4.2)             # 输出：4
float(5)              # 输出：5.0
float(3.14)         # 输出：3.14






Variable （变量）

数学中的变量：
Y = X + 12



计算机中的变量：Sometimes it is expedient to give values a name. These names are called variables. 

Example:
Y = 12
X = 3
Z = Y + X


变量的命名方式

	变量名必须以字母、下划线( _ )开头，变量名不能以数字开头。
	变量名只能包含字母数字字符和下划线 (A-z、0-9 和 _ )。
	变量名区分大小写（age、Age 和 AGE 是三个不同的变量）。

Exercise:
下列哪一个变量名是合法的？
Which of the following variable name is valid?
	0_counter
	__name
	rtn_98
	A_bc_def
	algo-ace
驼峰命名法

驼峰式命名法（Camel case）是一种不使用空格的书写方式，除了整个复合单词的首字母可以是大写或小写的之外，其他每个单词的首字母大写。
Example:
myStudentCount
SpeedUpEducation

 

蛇形命名法

蛇形命名法（snake_case）是指每个空格皆以下划线（_）取代的书写风格，
且每个单字的第一个字母皆为小写。

Example:
my_student_count
speed_up_education


Assignment Operator

Example:

x = -2
y = 3
q = x // y
r = x % y

Consider the following code:

X = 2
Y = X
Y = 3

 
Note:
	赋值运算符（=）不是在判断左右是否相等，而是将等号右边的值赋给左边
	赋值运算符的左边一定是变量名，不可以写1 = 1。
	变量的名称没有意义，不是说你给它起名叫apple_counter他就能自己帮你数苹果
	虽然名称没有意义，但好的编程习惯是，尽量让变量名与它所代表的值的实际意义吻合
	可以有多重赋值运算符，比如：
x, y = 1, 2
x, y = [1, 2]
x, y = (1, 2)

会给x赋值为1，y赋值为2

Exercise:
1. What does `print(21/3)` print on the computer monitor screen?
2. What does `print((18 // 3 + 6 * 5) % 11)` print on the computer monitor screen?
3. What does `print(2 + 3 * 4 - 7 % 3)` print on the computer monitor screen?
4. Is Python case sensitive when dealing with identifiers? 
5. How many distinct numbers can I represent with 1 byte? These numbers range from ______ to _______
6. What is the value of the 'x' determined by the expression given below? 
x = 40+8/2*2//-2

1. Which of the following is an invalid Python statement? 
	_a_b_c = 1000000
	a,b,c = 1000, 2000, 3000 
	abc = 1000000
	a b c = 1000 2000 3000 
	What is x, y, z after entering the following?
 








Week 1 Questions

 










There are N students from the University of Toronto going on a trip to Niagara Falls.
Each bus can carry 40 students.
Write a Python expression to calculate how many buses are needed.
Do not use any conditional statements, as you haven't learned them yet.
Provide three different methods. Be careful with data types.

