Group

Group
If G is a set and · is a binary operator, the pair (G,·) is said to be a group
if it satisfies the following three properties:
• [Associativity] 结合律
For every a,b,c ∈ G, a · (b · c) = (a · b) · c.
• [Identity] 单位元
There exists an element e ∈ G such that e · a = a · e = a for all a ∈ G.
• [Inverses] 逆元
For every a ∈ G, there exists a b ∈ G such that
a⋅b=b⋅a=e
We often write the inverse of a as a^(-1)
Example:
Prove that (R,·) 是一个Group

	R满足交换律，在实数域中
a · (b · c) = (a · b) · c.
	R中有乘法单位元 1，满足 for all x∈R
x*1=1*x=x
	R 中每个单位都有乘法逆元
x*1/x=1

Note：
其实群还暗含闭合性，因为这个乘法是G· G→G，也就是说，群内的任意元素做operation，结果应该还在群内
Example:
Prove that (N,·) 是一个Group





Example:
Prove that (R,+) 是一个Group

Solution
	R满足结合律，在实数域中
a+(b+c)= (a+ b)+c.
	R中有单位元 0，满足 for all x∈R
x+0=0+x=x
	R 中每个单位都有逆元
x+(-x)=0



Note:
如果一个群(G, ·)是正常群
	ab^(-1) ba=aa 用了哪一条定律
	bab^(-1) 能否等于 a?
	(ab)^2=a^2 b^2 吗?
	(ab)^(-1)=b^(-1) a^(-1)吗?


Abelian （阿贝尔群）
A group (G, ·) is said to be be abelian if the group operation is commutative; namely, for every a,b ∈ G we have a · b = b · a



Example：
常见的阿贝尔群：
阿贝尔群有两种主要运算符号——加法和乘法。

但是减法和除法，因为
a\b≠ b \ a

所以减法和除法不符合阿贝尔群的性质



Note:
如果一个群(G, ·)是阿贝尔群
	bab^(-1) 能否等于 a?
	(ab)^2=a^2 b^2 吗?
	(ab)^(-1)=b^(-1) a^(-1)吗?






二面体群
Given a positive integer n ≥ 3, the dihedral group of order n, denoted D_n,
is the set of symmetries of a regular n-gon under composition

这其实看不太明白

Example:
If r represents the rotation of the triangle by 120^o and 
If s is the reflection about the vertical axis, then 
D_3  ={e,r,r_2,s,sr,sr_2}
	
 


Question: 
Is this group abelian!

No, sr≠ rs.


Question: 
D_3  ={e,r,r_2,s,sr,sr_2}
中有6个元素，那么D_4 中要有几个元素呢？

Answer：
D3: 
ABC, BCA，CAB, 
ACB, CBA, BCA
6

D4: 
ABCD, BCDA, CDAB, DABC
BADC, ADCB, DCBA, CBAD
8
















Theorem:
If (G, ·) is a group, then the identity element is unique.

Proof:
假设我们不光有mult identity 1 ，z也是一个add identity, 那么意味着z加谁都是本身
zx=x for all x in F
因为假设x的mult inverse为 x^(-1) ，那么我们有：
1=x*x^(-1)
因此：
1=(zx) x^(-1)
1=z(xx^(-1))
1=z
1=z
Contradiction


Theroem
If (G, +) is a Group then identity elements are unique.

假设我们不光有add identity 0 ，z也是一个add identity, 那么意味着z加谁都是本身
z+x=x for all x in F
因为假设x的addition inverse为 -x ，那么我们有：
0=x+(-x)
因此：
0=(z+x)+(-x)
0=z+x+(-x)
0=z+0
0=z
Contradiction



Theroem
If (G, ·) is a Group then inverse elements are unique.


Part 2: Mult inverse is unique

假设对于x不光有mult inverse x^(-1) ，z也是一个mult inverse, 那么意味着
zx=1 
xx^(-1)=1 

那么
zxx^(-1)=x^(-1)  
z*1=x^(-1)  
z=x^(-1)  
Contradiction

Theroem
If (G, +) is a Group then inverse elements are unique.


Part 1: Additional inverse is unique
假设对于x不光有mult inverse -x ，z也是一个mult inverse, 那么意味着:
z+x=0 
x+(-x )=0 

那么
z+x+(-x )=(-x ) 
z+0=(-x ) 
z=(-x ) 
Contradiction



Theorem
Prove if a,b∈G, then (ab)^(-1)=b^(-1) a^(-1)

Proof:
因为 G是群，所以 a,b都有逆元 a^(-1),b^(-1)∈G。
计算：
(ab)(b^(-1) a^(-1))=a" "(bb^(-1))" " a^(-1)=aea^(-1)=aa^(-1)=e.
因此
(ab)(b^(-1) a^(-1) )=e
(ab)^(-1) (ab)(b^(-1) a^(-1) )=(ab)^(-1)
e(b^(-1) a^(-1) )=(ab)^(-1)
(b^(-1) a^(-1) )=(ab)^(-1)

















Order of Group

Order of Group
Given a group G, the order of G is its cardinality |G|. 

Order of Element
Given an element g ∈ G, the order of g, denoted similarly as |g|, is the smallest n ∈ Z^+ such that g^n  = e. If no such n exists, then |g| = ∞

Example
Consider the Group G={1_8,3_8,5_8,7_8 }, then we have |G|=4
|1_8 |=1,|3_8 |=2,〖|5〗_8 |=2,〖|7〗_8 |=2






Consider the Group G={1_5,2_5,3_5,4_5 }, then
1_5=1,2_5=4,3_5=4,4_5=2



Question
Why n∈Z^+, instead of n∈Z^*?

g^0  = e



Proposition: 
lf G is a group and a∈ G is the only element of G with order 2, then ab = ba for all b∈G.

Fix some b∈G. 

If b=a then ab=ba, 因此我们只需要考虑不等的情况 

Thus consider the element x=bab^(-1)（常见构造）. 

Note that x≠e, since if this were the case then x=e=bab^(-1) which implies that a=e, which is not possible since e has order 1. Now if we square x we get
x^2=(bab^(-1))(bab^(-1))=ba^2 b^(-1)=e.
Thus x must have order 2, from which it follows that x=a. 

But note that if x=a then bab^(-1)=a, from which we get that ab=ba. （两边同乘b^(-1)）.













Theorem
If G is a group and g ∈ G has order n, then g^k  = e for some k ∈ Z^+ if and only if n | k

Proof:
Part 1: If n | k, then g^k  = e for some k ∈ Z^+

Since n | k, there exists some integer s, such that ns=k, thus
g^k=g^ns=(g^n )^s=e^s=e

Part 2: If g^k  = e for some k ∈ Z^+, then n | k

Since g ∈ G has order n, thus g^n=e, 同时，n∈Z^+ is the smallest number can give the identity.

考虑k∈G, 也满足g^k=e，因为n是最小的，所以k≥n. 那么根据the divisior algorithm, k=nq+r,r∈[0,n)

e=g^k=g^(nq+r)=e^1 g^r=g^r
但是n∈Z^+ is the smallest number can give the identity，r∈[0,n)，因此，r只可能为0，因此k=nq→n|k










SubGroup
If (G,·) is a group and H ⊆ G, we say that H is a subgroup of G if (H,·) is a group. In this case, we write H ≤ G. If H = G, we instead write H < G

Which of the following is not a subgroup of Z_12 under addition?

	{0_12,6_12 }
	{0_12,4_12,8_12}
	{0_12}
	{0_12,2_12,6_12,10_12}


Subgroup Test (经常用到)
Suppose that G is a group and H ⊆G is non-empty. If for all a,b∈H we
have ab^(-1)  ∈H, then H ≤G (under the same binary operation).
Proof. 
We need to show that H is a group under the same operation as G.
[Associativity] Since H ⊆G, it follows that the operation is associative on H
as well.

[Identity] The identity element e ∈G is also in H. Since H is non-empty, choose some h∈H. From the hypothesis, let a= b= h so that e= aa^(-1)  ∈H, as required.

[Inverses] Fix some h ∈H and set a= e,b= h, so that the hypothesis tells us that h^(-1)  = eh^(-1)  ∈H, showing that H contains h^(-1)
.


Example:
Let G be a group and fix some element g ∈ G. 
Define the set H ={h ∈ G∶ hgh^(-1)  = g}. Show that H ≤ G.
Solution:
Let a,b∈H, then by definition aga^(-1)=g,bgb^(-1)=g. 
By Subgroup Test, we need to prove (ab^(-1) )∈H. By definition of H, we need to show
(ab^(-1) )g((ab^(-1) ))^(-1)=g


(ab^(-1) )g(ab^(-1) )^(-1)=(ab^(-1) )gba^(-1)  (since (b^(-1) )^(-1)=b)
=a(b^(-1) gb) a^(-1)
=aga^(-1)
=g

Thus H≤G




















Cyclic Group
A group G is cyclic if there exists a g ∈ G such that G = {g^n: n ∈ Z}. In this case, g is said to generate G. 
If G is a (not necessarily cyclic) group and g ∈ G, then the cyclic subgroup generated by g is ⟨g⟩ = {g^n: n ∈ Z}
The cyclic subgroup generated by g is ⟨g⟩= {g^n ∶ n∈Z}, such that 
|⟨g⟩|=|g|

隐含意义：如果一个element的order = size of n, then the element is the generator.
Example:
Z_4=⟨1_4 ⟩, 因为1_4 能generate 出：

1_4+1_4=2_4
1_4+1_4+1_4=3_4
1_4+1_4+1_4+1_4=0_4

当所有Z_4 中的元素都能被generate时，我们可以说1_4 是一个generator
当然3_4 也是一个generator


Example:
The cyclic subgroup generated by 2_4 is
G={0_4,2_4}


2_4就不是一个generator



Example:
Consider the group Z_6 under addition. How many elements of Z_6 generate Z_6 as a cyclic group?
1_6
 5_6,





























More Shit
Example
If (Z,⋅) is a Group and x,y ∈ G satisfy x⋅y = 0, then either x = 0 or y = 0.

Proof by contradiction
	xy = 0
	且 x ≠ 0
	且 y ≠ 0
因为 x,y 都是非零整数，所以 |x| ≥ 1 且 |y| ≥ 1。
因此
∣xy∣=∣x∣⋅∣y∣≥1⋅1=1.

也就是说
∣xy∣≥1.

但题目给 xy = 0，即
∣xy∣=0.

这与上式矛盾。
因此假设不成立，推得：
▭(x=0"   or   " y=0.)


A Group with Two Elements
G =({0,1},+) 


+	0	1
0		
1		

Answer:
+	0	1
0	0	1
1	1	0

G =({0,1},⋅) 

⋅ 	0	1
0		
1		

Answer:

⋅ 	0	1
0	0	0
1	0	1





A Group with Three elements

因为有加法Identity 0的存在，所以可以填上如下：

+	0	1	x
0	0	1	x
1	1		
x	x		

这个时候我们考虑1 + x 这个格子，1 + x的值只能是 0， 1， x
那么他能等于1吗？
如果1 + x等于1，1+0也等于1，那就意味着1有两个加法identity，所以不能等于1
那么他能等于x吗？
如果1 + x等于x, 0+x 也等于x，那就意味着x有两个加法identity，所以不能等于x
因此，这个格子只能填0
那么根据对称性，x+1也是0

+	0	1	x
0	0	1	x
1	1		0
x	x	0	







Example (往届原题 – 填空)
Let G = ({0,1,x},+) be a Group with three elements. Then (x + 1) + x is equal to?



































Example:
Show that a group G is abelian if and only if (ab)^(-1) = a^(-1) b^(-1) for all a,b∈G.


Answer：

Step 1：
If G is abelian then (ab)^(-1) = a^(-1) b^(-1)
	对任意群都成立的定理：(ab)^(-1)ⓜ=b^(-1) a^(-1) ┤。
	G是阿贝尔群，所以上面的运算是可交换的：对任意 x,y∈G，有 xy=yx。特别是对 x=a^(-1),y=b^(-1)也成立。
于是：
(ab)^(-1)ⓜ=b^(-1) a^(-1)ⓜ=a^(-1) b^(-1) ┤
Step 2:
If (ab)^(-1) = a^(-1) b^(-1)， then G is abelian
假设条件：
(ab)^(-1)=a^(-1) b^(-1)∀a,b∈G.┤

(ab)^(-1)=b^(-1) a^(-1)∀a,b∈G.┤
于是把两个式子放在一起，对任意 a,b∈G有：
b^(-1) a^(-1)=(ab)^(-1)=a^(-1) b^(-1).
所以我们得到：
b^(-1) a^(-1)=a^(-1) b^(-1).

现在对这个等式两边都取逆元（因为在群里，等式两边相等 ⇒ 其逆元也相等）：
(b^(-1) a^(-1) )^(-1)=(a^(-1) b^(-1) )^(-1).┤
利用你已经证明过的“乘积的逆元”公式：
(xy)^(-1)ⓜ=y^(-1) x^(-1) ┤

对左边取 x=b^(-1),y=a^(-1)，对右边取 x=a^(-1),y=b^(-1)，得到：
	左边：(b^(-1) a^(-1) )^(-1)=(a^(-1) )^(-1) (b^(-1) )^(-1)=ab┤;
	右边：(a^(-1) b^(-1) )^(-1)=(b^(-1) )^(-1) (a^(-1) )^(-1)=ba┤。
所以
ab=ba∀a,b∈G.

























Example:
If G is a group, define Z(G) = {a∈G: ab= ba,∀b∈G}. Show that Z(G) ≤G.

Answer：
•  Z(G)非空；
•  对所有 a,b∈Z(G)，有 ab^(-1)∈Z(G)。
Step 1
单位元 e一定在 Z(G)中：
对任意 g∈G，
eg=ge=g.

所以 e与所有元素都交换，故 e∈Z(G)。
Step 2
取任意 a,b∈Z(G)。我们要证明：
∀g∈G,(ab^(-1))g=g(ab^(-1)).

因为 a,b∈Z(G)，它们跟所有元素都可交换：
	ag=ga对所有 g∈G；
	bg=gb对所有 g∈G。
由此也可以得到它们的逆元同样可交换：
	b^(-1) g=gb^(-1)，因为从 bg=gb两边左乘 b^(-1)得：
g=b^(-1) gb⇒b^(-1) g=gb^(-1).
现在对任意 g∈G计算：
■((ab^(-1))g&=a(b^(-1) g)@&=a(gb^(-1))("因为 " b^(-1) g=gb^(-1))@&=(ag)b^(-1)@&=(ga)b^(-1) ("因为 " ag=ga)@&=g(ab^(-1)).)

于是对所有 g∈G都有
(ab^(-1))g=g(ab^(-1)),

这说明 ab^(-1)与 G中所有元素都交换，所以
ab^(-1)∈Z(G).
















Example:

Let G be a group and a ∈G have order |a|= n. For any k ∈Z+, show that ⟨a^k⟩= ⟨a^gcd(k,n) ⟩.
Answer：
Remark If a^k是 a^d的一个幂，所以由生成子群的定义可知：
a^k=(a^d )^m∈⟨a^d⟩.
Let
d=gcd⁡(k,n).
Recall the definition of cyclic subgroup:
⟨a^k⟩={(a^k )^m:m∈Z},⟨a^d⟩={(a^d )^m:m∈Z}.
Step 1: ⟨a^k⟩⊆⟨a^d⟩,
因为 d=gcd⁡(k,n)，所以 d整除 k。
于是存在整数 t∈Z使得
k=dt
对任意 m∈Z：
(a^k )^m=a^km=a^dtm=(a^d )^tm∈⟨a^d⟩.┤

所以
⟨a^k⟩⊆⟨a^d⟩.


Step 2: ⟨a^k⟩⊆⟨a^d⟩,
这里用到 Bézout 恒等式：
因为 d=gcd⁡(k,n)，存在整数 r,s∈Z使得
d=rk+sn.
对两边取 a的幂：
a^d=a^(rk+sn)=a^rk a^sn=(a^k )^r (a^n )^s.
但 ∣a∣=n，所以
a^n=e⇒(a^n )^s=e^s=e.
因此
a^d=(a^k )^r e=(a^k )^r.

这说明 a^d是 a^k的一个幂，于是
a^d∈⟨a^k⟩.
同理，对任意 m∈Z：
(a^d )^m=((a^k )^r )^m=(a^k )^rm∈⟨a^k⟩.┤

所以
⟨a^d⟩⊆⟨a^k⟩.
由这个结论可以推出元素 a^k的阶为
∣a^k∣=n/(gcd⁡(k,n)),


Homomorphisms

Definition：homomorphism （保持运算结构的映射）
Given two groups (G,·) and (H,⋆), a function ϕ: G→H is said to be a group homomorphism if for all x,y∈G, ϕ(x·y) = ϕ(x) ⋆ϕ(y).

Note:
其实你可以把它理解为
ϕ(xy)=ϕ(x)ϕ(y)

Example：
Determine whether the map ϕ∶(Z_6,+) →(Z_12,+) given by ϕ([x]_6) = [2x]_12 is a group homomorphism.
Solution
ϕ([a]_6  + [b]_6 )= ϕ([a+ b]_6 )
= [2(a+ b)]_12  
= [2a]_12  + [2b]_12  
= ϕ([a]_6) + ϕ([b]_6),
Is this proof compete?
Consider ϕ([x]_6) = [3x]_12, 那么This map is not well-defined
[1]_6=[7]_6
那么按理说
 ϕ([1]_6 )  =ϕ([7]_6 )
但是
 ϕ([1]_6 )=[3]_12,ϕ([7]_6 )=[9]_12  

因此，你还要证：
If [a]_6= [b]_6, then ϕ([a]_6 )=ϕ([b]_6)

Suppose that [a]_6= [b]_6, so that a-b = 6k for some k∈Z. Now ϕ([a]_6)-ϕ([b_6 ]) = 2[a]_6-2[b]_6  = 2([a]_6-[b]_6) = 12k, showing that
ϕ([a]_6) ≡ϕ([b]_6 )(mod 12)
Example：
Determine whether the map ϕ∶(Z,+) →(Z,+) given by ϕ(x) = x^2 is a group homomorphism.

φ(a+b)=(a+b)^2=a^2+2ab+b^2

φ(a)+φ(b)=a^2+b^2


Kernel and Image
Given a group homomorphism ϕ: G→H, we define the
• kernel of ϕ as ker(ϕ) = {g∈G: ϕ(g) = e_H  }, where e_H is the identity element in H;
• image of ϕ as im(ϕ) = ϕ(G) = {ϕ(g)∶ g∈G}, which is our usual notion of the image of a function.

Example
Consider the map ϕ: Z_12  →Z_6 given by ϕ([x]_12) = [2x]_6. Determine the kernel and image of this map.

Solution
ker(ϕ) = {[0]_12,[3]_12,[6]_12,[9]_12} 

im(ϕ) = {[0]_6,[2]_6,[4]_6}.






Theorem
Suppose that ϕ: G→H is a group homomorphism.
1. ϕ(e_G) = e_H , where e_G and e_H are the identity elements of G and H respectively.
2. For any n∈Z,ϕ(g^n )= ϕ(g)^n. Notably, ϕ(a^(-1) )= ϕ(a)^(-1)
3. For any g∈G such that |g|<∞, |ϕ(g)| divides |g|.
4. ker(ϕ) ≤G and im(ϕ) ≤H.
5. If K ≤G then ϕ(K) ≤H.
6. If K is a cyclic subgroup of G then ϕ(K) is a cyclic subgroup of H.
7. If K is an abelian subgroup of G then ϕ(K) is an abelian subgroup
of H.
8. If L≤H then ϕ^(-1) (L) ≤G.
9. ϕ is injective if and only if ker(ϕ) = {e_G}.

Example: Proof of (8)
Fix a,b ∈ϕ^(-1) (L): 证明目标ab^(-1)  ∈ϕ^(-1) (L), 也就是要证明 ϕ(ab^(-1)) ∈L

Since a,b ∈ϕ^(-1) (L), thus ϕ(a),ϕ(b) ∈L by definition. Since L ≤H that means that ϕ(b)^(-1)  ∈L as well. （因为L是一个群，因此所有元素的逆元要在群里）

ϕ(ab^(-1)) = ϕ(a)ϕ(b^(-1)) (ϕ a homomorphism)
= ϕ(a)ϕ(b)^(-1)  (by property 2)


Since ϕ(a)ϕ(b)^(-1) are elements of L and L is a group, it follows that ϕ(ab^(-1)) ∈L. （因为G×G→G）

Thus ab^(-1)  ∈ϕ^(-1) (L), as required.

Isomorphic

Definition：isomorphism and isomorphic （同构）
If G and H are two groups, we say that a group homomorphism ϕ: G→H is an isomorphism if ϕ is also a bijection. 
If an isomorphism between G and H exists, then we say that G and H are isomorphic and write G≅ H.

两个群同构，意思是它们“完全一样”，只是外表不同。
结构相同、运算行为相同，只是元素名字不一样。

Example：
Z_2={0,1}_2≅⟨[2]_4⟩

⟨[2]_4⟩是由2生成的循环子群
⟨[2]_4 ⟩={0,2}_4

那么其实他们的运算规则完全一样，这里画表，然后展示
	Z_2里的0就是⟨[2]_4 ⟩里的0
	Z_2里的1就是⟨[2]_4 ⟩里的2
Question：
怎么证明两个群同构呢？

Answer：
找bijection, 并证明homomorphism
ϕ(x):{0,1}→{0,2}, such that
ϕ(x)={█(■(0&if x=0)@■(2&if x= 1))┤
同时你要证明ϕ(x) is homomorphism，也就是证明
ϕ(a+b)=ϕ(a)+ϕ(b)
Theorem
Suppose that ϕ: G→H is an isomorphism, so that G and H are isomorphic through ϕ. Then the following is True:
1. ϕ^(-1) ∶ H →G exists and is an isomorphism.
2. G is abelian if and only if H is abelian.
3. G is cyclic if and only if H is cyclic.
4. If K ≤G then ϕ(K)≅ K.
5. For all g∈G,|g|= |ϕ(g)|.
6. |G|= |H|


Exercise:
Which of the following statements is false?
	If any group homomorphism ϕ:G→H is injective, then G≅ϕ(G)
	For any Group G≅G
	If G and H are groups such that G ≅ H, then any homomorphism ϕ:G → H is an isomorphism.
	If ϕ:G → H is an isomorphisms, and K ≤ G is abelian, then ϕ(K) is also abelian.

Answer:
C
A为什么对？因为任何函数都对自己的像满射，比如
f:R→Im(f),f(x)=x^2
A换个说法就是
ϕ:G→ϕ(G) is injective, then G≅ϕ(G)

Example: Proof of (2)
Suppose that ϕ: G→H is an isomorphism, so that G and H are isomorphic through ϕ. Then G is abelian then H is abelian.

Answer:

Suppose that G is abelian, and fix h_1,h_2  ∈H.

Since ϕ is bijective, there are g_1,g_2  ∈G such that ϕ(g_1) = h_1 and ϕ(g_2) = h_2. 
h_1 h_2=ϕ(g_1 )ϕ(g_2 )=ϕ(g_1 g_2 )
=ϕ(g_2 g_1 )
=ϕ(g_2 )ϕ(g_1 )=h_2 h_1

Thus H is abelian.


Automorphism（自同构）
Automorphism = Isomorphism from G to G itself.

Example：
{1,2,3,4,5}_6={5,2,3,1,4}_6

Example:
Z, 取ϕ(x)=-x







Question:
Determine whether each of the following a group homomorphism.

Example 1:
Let R^*= R \{0} be a group under multiplication. 
Define ϕ: R^*  →R^* by ϕ(x)= x^2

φ(xy)=(xy)^2=x^2 y^2=φ(x)φ(y).

.





Example 2:
ψ: Z_4  →Z_4,ψ([n]_4) = [n+ 1]_4.
反例：
ψ([0]_4+[0]_4)=ψ([0]_4)=[1]_4.
ψ([0]_4)+ψ([0]_4)=[1]_4+[1]_4=[2]_4.
[1]_4≠[2]_4 ┤






Question:
Determine the kernel for each of the following group homomorphisms. 

Example 1:

δ: Z →Z_6,δ(n) = [2n]_6.

Solution:
ker(δ)={n∈Z:n=3k, k∈Z}.


Example 2:

ρ: Z_12  →Z_4,ρ([n]_12) = [n]_4.

Solution:
ker(ρ)={[0]_12 ,[4]_12 ,[8]_12 }.








Question:
Suppose that ϕ∶ G →K is a homomorphism with ker(ϕ) = {e_G}. Show that G≅ ϕ(G).
Solution:
想要证明 G≅φ(G)，只需要证明这个 φ:G→φ(G)是一个 isomorphism，也就是：
	它是 homomorphism（已经给定）；
	它是 bijection（双射）。
Step 1: 证明 φ:G→φ(G)是 surjective
φ(G)的定义就是 {φ(g):g∈G}。
所以，对任意 y∈φ(G)，按定义，存在某个 g∈G使得
y=φ(g).

所以 φ:G→φ(G)按定义就是满射（surjective）
Step 2: φ(g_1)=φ(g_2)，那么 g_1=g_2。
取任意 g_1,g_2∈G，假设
φ(g_1)=φ(g_2).
我们来操作一下这个等式：
φ(g_1)=φ(g_2)⟹φ(g_1)φ(g_2 )^(-1)=e_K.
因为 φ是同态，有
φ(g_1)φ(g_2 )^(-1)=φ(g_1)φ(g_2^(-1))=φ(g_1 g_2^(-1)).



于是得到
φ(g_1 g_2^(-1))=e_K.
这说明
g_1 g_2^(-1)∈ker⁡(φ).
但题目给出
ker⁡(φ)={e_G},
所以
g_1 g_2^(-1)=e_G.

从这个推出
g_1=g_2.

因此，φ 是单射（injective）。






Question:
Let G be a group. Prove that ϕ∶ G →G,φ(g)=g^(-1)  is a homomorphism if and only if G is abelian.
Solution:
(⇒) 若 G是阿贝尔群，则 φ(g)=g^(-1)是同态
假设 G是 abelian，也就是：
xy=yx,∀x,y∈G.
我们要验证同态条件：
φ(xy)=φ(x)φ(y),∀x,y∈G.
左边：
φ(xy)=(xy)^(-1).

所以：
φ(xy)=(xy)^(-1)=y^(-1) x^(-1)=x^(-1) y^(-1)=φ(x)φ(y).

这就证明了：在阿贝尔群中，映射 g↦g^(-1)满足
φ(xy)=φ(x)φ(y),

因此是一个 group homomorphism




(⟸)若 φ(g)=g^(-1)是同态，则 G是阿贝尔群
假设 φ是群同态，也就是对所有 x,y∈G有：
φ(xy)=φ(x)φ(y).

把 φ(g)=g^(-1)代入同态条件，得到：
(xy)^(-1)=x^(-1) y^(-1),∀x,y∈G.┤

但对任意群，我们总有你之前证明的公式：
(xy)^(-1)ⓜ=y^(-1) x^(-1).┤

于是对所有 x,y∈G同时有：
y^(-1) x^(-1)=(xy)^(-1)=x^(-1) y^(-1).

利用 (ab)^(-1)ⓜ=b^(-1) a^(-1) ┤再一次：
	左边：(y^(-1) x^(-1) )^(-1)=(x^(-1) )^(-1) (y^(-1) )^(-1)=xy┤;
	右边：(x^(-1) y^(-1) )^(-1)=(y^(-1) )^(-1) (x^(-1) )^(-1)=yx┤.
所以我们得到：
xy=yx,∀x,y∈G.

这正是 G是阿贝尔群的定义。



Question:
Show that groups R and Q under addition are not isomorphic.
(R,+)≅(Q,+).

Solution:
No bijection between R and Q























Question:
Consider the group Q under addition. Show that for any non-zero q ∈Q, the map ϕ_q ∶ Q →Q, ϕ_q  (r) = qr is an automorphism of Q.

同态性质（Homomorphism）
(Q,+)的群运算是加法。
要验证同态，只需对所有 r_1,r_2∈Q证明：
φ_q (r_1+r_2)=φ_q (r_1)+φ_q (r_2).
计算：
φ_q (r_1+r_2)=q(r_1+r_2)=qr_1+qr_2=φ_q (r_1)+φ_q (r_2).
所以 φ_q是一个 group homomorphism
单射
如果 φ_q (r_1)=φ_q (r_2)，
即 qr_1=qr_2⇒q(r_1-r_2)=0⇒r_1-r_2=0，所以 r_1=r_2。

满射
取任意 s∈Q。我们要找 r∈Q使得：
φ_q (r)=s,"即 " qr=s.

因为 q≠0，我们可以令
r=s/q.
注意 q,s∈Q，而有理数对除法（分母非零）也封闭，所以 r=s/q∈Q。
于是：
φ_q (r)=q⋅s/q=s.

所以对任意 s∈Q，都存在 r∈Q使得 φ_q (r)=s，
⇒φ_q是 surjective


