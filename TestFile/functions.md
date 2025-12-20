Function

A function f from a set A to a set B is a rule, that assigns to each element a ∈ A, a unique element f(a) ∈ B, called the image of a under f.

The notation f∶ A → B means that f is a function with domain A and codomain B.

The set {f(a): a ∈ A}, denoted as f(A), is called the range (or the image) of the function f. Note that f(A) is always a subset of the codomain B.

Example:

We define a function f∶ [-3,4] → (-2,2) by f(x) = sin x

The image of π/2  is f (π/2  ) = sin π/2 = 1, and the image of -  π/6 is f ( -π/6  ) = sin ( -π/6  ) = - 1

The codomain of f is (-2,2)

The range of f is [-1,1]

Example:

The diagram below defines a function S∶ {a,b,c,d} → {1,2,3} .
 
The range of above function is {1,3}, the codomain of above function is {1,2,3}

 




 

使用竖直线检测可以快速的判断一个图像是否是一个函数



Graph of a function
The graph of a function f∶ A → B is the set {(a,f(a)): a ∈ A}.

Example:

 





















Inverse

Consider a function f : {a, b, c, d} → {α, β, γ, δ, ϵ}, given by the following diagram

 

Does this function have inverse?
 
In the new diagram, both c and d are assigned to the element γ. 

Functions cannot assign two images to an element in the domain.

In the new diagram, no elements are assigned to δ and ϵ. However, a function must assign an image to every element in its domain.

 

Question: 

Is this function injective? Is this function surjective?

 
                   A                                    B

Injective: B 中的每个值 y，都至多有一个x，使得f(x)=y （水平线检测）


Surjective: B 中的每个值 y，都至少有一个x，使得f(x)=y

In order to be able to invert a function, our initial function must be both injective and surjective.
Examples:
g, h and r are functions from a set A to another set B, given by the following diagrams
他们分别是injective，surjective 还是 bijective？

 


The function g is injective
	as there are no two elements in A which are mapped to the same element in B 
	g is not surjective as there is a "lonely" element in B, which is not the image of an element in A.


The function h is surjective, 
	as every element in B is an image, 
	but it is not one-to-one, since there are two arrows pointing to the same element in B.


The function r is both an injection and a surjection, 
	as every element in B is the image of exactly one element in A. 





Is following function injective and surjective

f∶ R → R,f(x)=1/(1 + x^2 )  .
g is not an injection. 这个举反例就好，
存在一个n_1≠n_2，那么g(n_1 )=g(n_2)
f(2)= f(-2)=1/5
g is not a surjection. 这个举反例就好，
因为f(x)>0, 因此没有能够让f(x)=-1 的x值，因此它不是surjection.







证明injection
g∶ N → N,g(n) = n^3  + 1.


g is an injection. 
其实就是在证明，如果n_1≠n_2，那么g(n_1)≠g(n_2)
或者证明：如果g(n_1 )=g(n_2)，那么n_1=n_2

We prove this by showing that distinct elements in the domain are mapped to distinct images. Indeed, if n_1,n_2 are two natural numbers, then
n_1^3≠n_2^3
n_1^3+1≠n_2^3+1
g(n_1)≠g(n_2)

证明bijection

h: R \ {-1}→ R \ {1},h(x)=  x/(x + 1).

h is a bijection. Here is the proof.

h is an injection.
To show that h is one-to-one, we start by assuming that h(x_1) = h(x_2) for some x1,x2≠ -1. We argue that x_1  = x_2 as follows.
h(x_1 )=h(x_2 )
x_1/(x_1+1)=  x_2/(x_2+1)
x_1 (x_2+1)=x_2 (x_1+1)
x_1=x_2

h is a surjective. 证明的思路是，对于任意的y（在函数的值域中），总能找到一个 x 使得 h(x) = y
Now we show that h is surjective. Let y≠ 1. Our task is to show that h(x) = y for some x in the domain of h. 

We do that by solving the equation h(x) = y for x:
x/(x+1)=y
x=(x+1)y
x=y/(1-y) (since y≠1)
这样我们就说明了，你随便给我一个y值，我能告诉你，想要得到这个y，x是多少
we showed that any y in the codomain of h has an ‘x’, which implies that h is surjective.
Monotone
We say that f is a strictly increasing (respectively decreasing) function, if for every x_1  < x_2 in A, we have f(x_1) < f(x_2) (respectively f(x_1) > f(x_2)). 

A function f is strictly monotone, if it is either strictly increasing or strictly decreasing.

 


Theorem
Let A ⊆ R. If f∶ A → R is a strictly monotone function, then f is injective.
(一定可以通过水平线测试)


Example:

Prove: the function f∶ (-1,1)→ R ,f(x)=2x/(1-x^2 )   is injective
 



Exercise:
Let g:Z×N→Z×N be given by g(m,n)=(3-m,n^2+1)

Part A: Is this function injective? Explain

Part B: Is this function surjective? Explain

 
















Exercise:

Let h:Z×Z→Z×Z be given by h(x,y)=(2xy,7x-3y)

Part A: Is this function injective? Explain

Part B: Is this function surjective? Explain

 















 









Composition
 
 





Is the order of Composition matter? If not, give me a counter example
Composition的顺序重要吗？如果不重要，请给我一个反例

 





假设f∶ A → B and g∶ B → C be two functions.

我能写g o f吗？







我能写fo g吗？














Relation between composition

Example

Let f∶ A → B and g∶ B → C be two functions. Prove that if g o f is injective, then so is f.

证明：如果 g o f 是 injective，那么f一定是injective


We do so by showing that f(x_1) = f(x_2) implies x_1  = x_2 for all x_1,x_2 ∈ A.

If f(x_1) = f(x_2), then, by applying the function g on both sides of this equality, we get

g(f(x_1 ))=g(f(x_2 )))
g o f(x_1 )=g o f(x_2 )



Since g o f is injective, thus, from g o f(x_1 )=g o f(x_2 ), we have that x_1  = x_2, This completes the proof of injectivity of f






Example

If the composition g o f is injective, must also g be injective?

Answer
不一定，下图就是一个例子


 











定理
The composition of two injections is an injection

Let f∶ A → B and g∶ B → C be two injections. Our task is to prove that g o f∶ A → C is also injection.

If (g∘f)(x_1)=(g∘f)(x_2) then:
g(f(x_1 ))=g(f(x_2 ))

Since g is injective, this implies:
f(x_1 )= f(x_2 )

Since f(x_1)=f(x_2) and f is injective, we have:
x_1=x_2

which shows that g o f is injective.













定理
The composition of two surjections is a surjection.

Proof
Let f∶ A → B and g∶ B → C be two surjections. Our task is to prove that g o f∶ A → C is also surjective

Let z ∈ C be an arbitrary element. 

As g is surjective, z = g(y) for some y ∈ B. Similarly, f is surjective, and so y = f(x) for some x ∈ A. 

Over all, we have

z = g(y)= g(f(x))= g o f(x)

which shows that g o f is surjective.









定理
If f∶ A → B and g∶ B → C are two bijections, then (g o f)^( -1)  = f^(-1)  o g^(-1)  .

Proof
Our task is to show that they are equal to each other. I.e., we need to prove that (g o f)^(-1)  (z) = f^(-1)   o g^(-1)  (z) for any z ∈ C

假设f(x)=y,g(y) = z, and denote y = g^(-1)  (z) and x = f^(-1)  (y). 

Therefore, 
f^(-1)  o g^(-1) (z)= f^(-1)  ( g^(-1) (z))=f^(-1) (y)=x

On the other hand
g o f(x)=g(f(x))=g(y)=z
Hence:
(g o f)^(-1) (z)=x





定理
The composition of two bijections is a bijection.




Cardinality

Cardinality
Two sets A and B are said to have the same cardinality, if there is a bijection between them.

想象一下你有两个篮子，一个篮子装了苹果，一个篮子装了橙子。如果你能把每个苹果都跟一个橙子一一对应起来，而且每个橙子都有对应的苹果，那么我们就可以说这两个篮子的“个数”是一样的。这里的“一一对应”就像是把两个篮子里的水果配对，每个水果都能找到搭档，没有剩下的。
这就是说两个集合“有相同的大小”或“同样多”，即使它们看起来不一样，但只要能配对上，就说明它们数量一样。这就是所谓“有相同的cardinality”。

Example:

A={Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday}

B ={1,2,3,4,5,6,7}

这两个集合具有相同的（cardinality），因为它们都包含七个元素。

More formally, we can easily construct a bijection f∶ A → B by defining
f(Sunday)=1,f(Monday)=2,…



Example:
The sets A = {x,y,z} and B = {ϕ} do not have the same cardinality. Because they do not have same number of elements.




Example:
A = N = {1,2,3,...}.

B = {-1,-2,-3,...}.

Define a function f∶ A → B by f(n) = -n can “pair” elements of one set with elements from the other set.



A set, that has the same cardinality as N, is called a countable set. 
具有与 N 相同或者小于N的cardinality的集合称为可数集。

An infinite set that is not countable, is called an uncountable set.
不可数的无限集称为不可数集。



Is following set countable?
	N itself 
	The rational numbers Q 
	The negative integers 
	The even positive integers 
	The set of all integers Z 
	N × N

N是可数的
Z是可数的
The negative integers 是可数的
N × N是可数的
Q是可数的

R是不可数的

总结
当你要证明一个infinite的东西是countable的时候，你需要证明，他跟N之间存在一一对应的关系

比如A=N= {1,2,3,…}, B={-1,-2,-3,…}
那么有一个function： g:A→B, g(n)= -n
比如A=N= {1,2,3,…}, B={2,4,6,…}
那么有一个function： g:A→B, g(n)= 2n
但是为什么Q是可数的呢？
Example Proof: The rational numbers Q is countable

当你要证明一个infinite的东西是countable的时候，你需要证明，他跟N之间存在一一对应的关系

那么我们怎么把N和Q一一对应呢？

我们把所有的小数按照这样的顺序排列：
 

We define, for each k ∈ N, the set
A_k={1/(k-1),2/(k-2),…,(k-1)/1}

这个时候你可以发现，这里面常多的重复，比如：
1/2 , from A_3, is repeated as 2/4 in A_6
我们删除掉这些重复：
 

而后我们把去重后的数列按顺序编号为a_1,a_2,a_3,... (for instance, a1 =1/1  ,a_4  =1/3  ,a_6  =1/4  ,a_11  =5/1 , etc.


那么这个新数列可以存在下面的两个属性：
	There are no repeated numbers. （没有重复的玩意）
	Every positive rational number appears as an element of the sequence. （这里面一定包含所有的正有理数）

然后，我们把负有理数和0也添加进来，这样他就包含了所有的正有理数，负有理数，和0
 

As we now have a sequence, containing all the rational numbers, and without any repetitions, we can define a function f:N→Q  according to the following

 


In conclusion, we have constructed a bijection from N to Q, and so these two sets have the same cardinality.








定理
The set of natural numbers, N, and the set of rational numbers, Q, have the same cardinality.


Question:

Do there exist infinite sets which are not countable?


The set of real numbers R is uncountable.


Proof
Reduction: prove that (0, 1) is uncountable.

suppose that f∶ N → (0,1) is a bijection. Then, for each n ∈ N,f(n) is some real number between 0 and 1, whose decimal expansion must start as 0.______ . If the decimal expansion happens to be finite (such as 0.25), zeros can be added to make it infinite (0.250000 . . .).

 
To prove that f is not a surjection, we now create a real number, in the interval (0,1), that is not the image of any n ∈ N under f.

Define a number x ∈ (0, 1), with decimal expansion 0.a_1 a_2 a_3 a_4 a_5  ..., as follows:
 
then the number x begins as 0.454544 ....
In other words, we look at the digits on the diagonal of the above array, and pick the k-th digit of x to be either 5 (if the corresponding digit on the diagonal is 4) or 4 (in all other cases).

The number x is defined in such a way that its k-th digit is different than the k-th digit of f(k), and therefore x≠ f(k) for all k ∈ N. Consequently, x is a real number in (0, 1) that does not appear in the list f(1),f(2),f(3),..., and so f is not surjective. This contradicts the fact that f is a bijection, and hence R must be uncountable. This concludes the proof of the theorem.






























看不懂？没关系，我们把它简化一下：

想象我们有一个无穷大的表格。有人跟我们说：“我可以把所有在 (0,1) 里的小数都写进这个表格里，每个小数都占一行，每行对应一个自然数。这样，我们就能把这些小数一一列出来啦！”

f(1)	0.3928343...
f(2)	0.1456320...
f(3)	0.5955251...
f(4)	0.1204397...
f(5)	0.1052296...

他说他写了所有的数，但我们不信！我们觉得他一定漏了某些数。于是我们玩了个小把戏：我们故意制造一个他绝对没写到的数。

我们从表格的“对角线”入手，每行挑一个数字：
	从第一行挑第1个数字。
	从第二行挑第2个数字。
	从第三行挑第3个数字。 ...
比如，刚才表格的对角线是
第1行的第1个数字：3 
第2行的第2个数字：4 
第3行的第3个数字：5 
第4行的第4个数字：4 
第5行的第5个数字：9
然后，我们把这些数字换一换：
	如果数字是 4，就换成 5；
	如果不是 4，就换成 4。
这样，我们得到一个全新的数，比如：
新数：0.45454...

这个数有什么特别呢？它和表格里每一行的数都不同！
为什么这个数一定不在表里？
	它和第1行不一样，因为它的第1位和第1行的第1位不同。
	它和第2行不一样，因为它的第2位和第2行的第2位不同。
	它和第3行不一样，因为它的第3位和第3行的第3位不同。 
	...

如果我们总能制造出一个不在表里的数，就说明这张表不可能包含所有的 (0,1) 里的数。















Exercise：

 

A = {x|5x+1∈Q}
B = {0,2,-2,4,-4,8,-8,…}
如果想要证明他们有相同的cardinality，那么我们得任选一条证明：
	存在一个bijection f:B→A
	存在一个bijection f:A→B
	A和N有相同的cardinality，B和N有相同的cardinality

首先，我们有一个Bijection from Q to A, 
f:Q→A,f(x)=(x-1)/5
根据定理，我们也有一个bijection from N to Q, 假设这个bijection 为 g：
g:N→Q
那么
f o g
是一个Bijection from N to A, 因此，A和N有相同的cardinality

然后我们考虑是否B和N有相同的cardinality，将B中的所有元素这么排列，这里面没有重复的元素：
0,2,-2,4,-4,8,-8,…
然后我们定义一个新函数
ϕ:N→B,ϕ(n)=n th item in above sequence 

因此，A和B有相同的cardinality
Schr¨oder-Bernstein Theorem

Let A and B be two sets. If |A| ≤ |B| and |A| ≥ |B|, then |A| = |B|.


换句话说：
如果我们有一个两个injection f∶ A → B， 有一个g：B → A
那么我们就有一个bijection h: A → B.
 
Example
证明 |[0, 1]| = |(0, 1)|

Define functions f : (0, 1) → [0, 1] and g : [0, 1] → (0, 1) as follows:

f(x) = x for  0 < x < 1
g(x)=x/2  +1/4  for 0 ≤ x ≤ 1 .

