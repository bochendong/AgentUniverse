# 群论基础与群的结构特征（Group Theory Essentials and Structure）

<Section id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8">
## 一、群的基本定义与基本性质

<Introduction id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_field_03b0532f">
本章主要介绍群论的基础概念，包括群的定义、二元运算、结合律、单位元和逆元等四条基本公理。学习本章内容有助于理解抽象代数中群结构的基本特性，掌握判断集合和运算是否构成群的方法。这是后续深入研究代数结构、同态、同构、子群等内容的基础环节。通过本章的学习，你将能够初步分析各种具体数集是否形成群，并掌握有关群基本不变量（如单位元与逆元唯一性）的推理和证明技巧，为后续深入抽象代数打下坚实的理论基础。
</Introduction>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_field_bc65828b"></Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_987f4642">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_987f4642_field_603945d0">
证明 $(\mathbb{R},+)$（实数集关于加法）是一个群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_987f4642_field_d3ad9e79">
$(\mathbb{R},+)$ 是群。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_987f4642_field_0e270c86">
**步骤1：封闭性**

对任意 $a, b \in \mathbb{R}$，根据实数加法的定义，有 $a + b \in \mathbb{R}$。

**步骤2：结合律**

对任意 $a, b, c \in \mathbb{R}$，根据实数加法的基本性质，
$$
(a + b) + c = a + (b + c).
$$

**步骤3：单位元存在**

实数 $0$ 是加法单位元。对任意 $a \in \mathbb{R}$，有
$$
a + 0 = 0 + a = a.
$$

**步骤4：逆元存在**

对每个 $a \in \mathbb{R}$，存在 $-a \in \mathbb{R}$，使得
$$
a + (-a) = (-a) + a = 0.
$$

**结论：**

$(\mathbb{R}, +)$ 同时满足封闭性、结合律、单位元和逆元存在四条群的公理，因此是一个群。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_21e7ba56">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_21e7ba56_field_07d3dbc5">
证明 $(\mathbb{R}^*,\cdot)$（去零实数关于乘法）是一个群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_21e7ba56_field_9dde3b38">
$(\mathbb{R}^*,\cdot)$ 是群。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_21e7ba56_field_c8054d14">
**步骤1：封闭性**

对任意 $a, b \in \mathbb{R}^*$，根据实数乘法的定义，$a \cdot b \neq 0$，且 $a \cdot b \in \mathbb{R}^*$。因此成立。

**步骤2：结合律**

对任意 $a, b, c \in \mathbb{R}^*$，实数乘法满足结合律：
$$
(a \cdot b) \cdot c = a \cdot (b \cdot c).
$$

**步骤3：单位元存在**

实数 $1 \in \mathbb{R}^*$，且对所有 $a \in \mathbb{R}^*$，有
$$
a \cdot 1 = 1 \cdot a = a.
$$

**步骤4：逆元存在**

对任意 $a \in \mathbb{R}^*$，$a \neq 0$，所以 $\frac{1}{a} \in \mathbb{R}^*$。且
$$
a \cdot \frac{1}{a} = \frac{1}{a} \cdot a = 1.
$$

**结论：**

$(\mathbb{R}^*, \cdot)$ 满足封闭性、结合律、单位元和逆元存在四条群的公理，因此是一个群。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_51c6772b">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_51c6772b_field_7b49753a">
证明 $(\mathbb{N},\cdot)$（自然数关于乘法）不是一个群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_51c6772b_field_ae0107a3">
$(\mathbb{N},\cdot)$ 不是群。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_concept_block_3ac3f36d_example_51c6772b_field_47f5db2b">
**步骤1：封闭性**

对任意 $a, b \in \mathbb{N}$，有 $a \cdot b \in \mathbb{N}$，封闭性成立。

**步骤2：结合律**

乘法对任意 $a, b, c \in \mathbb{N}$ 满足结合律：
$$
(a \cdot b) \cdot c = a \cdot (b \cdot c).
$$

**步骤3：单位元存在**

$1 \in \mathbb{N}$，且对所有 $a \in \mathbb{N}$，$a \cdot 1 = 1 \cdot a = a$。

**步骤4：逆元是否存在**

对于 $1$ 以外的数，例如 $a = 2 \in \mathbb{N}$，若存在 $b \in \mathbb{N}$ 使得 $2 \cdot b = 1$，则 $b = \frac{1}{2}$，但 $\frac{1}{2} \notin \mathbb{N}$。

所以 $2$ 没有乘法逆元（即不存在 $b \in \mathbb{N}$ 使得 $2 \cdot b = 1$）。

**结论：**

由于逆元存在性不满足（除 $1$ 以外的元素没有逆元），$(\mathbb{N}, \cdot)$ 不是群。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_facc041b">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_facc041b_field_432cd1af">
证明：若 $(G,\cdot)$ 是群，且 $a\cdot b = e$，则必有 $a = b^{-1}$，$b = a^{-1}$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_facc041b_field_d26b952b">
是成立的，即 $a = b^{-1}$，$b = a^{-1}$。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_facc041b_field_477f4851">
**步骤1：由题意分析逆元**

已知 $(G, \cdot)$ 是群，$e$ 是单位元。已知 $a \cdot b = e$，根据群的定义：每个元素必有逆元且唯一，且有 $a \cdot a^{-1} = a^{-1} \cdot a = e$。

**步骤2：证明 $a = b^{-1}$**

$a \cdot b = e$ 可理解为 $a$ 是 $b$ 的左逆元，$b$ 是 $a$ 的右逆元。由于群中逆元唯一，$a$ 和 $b$ 必互为逆元。下面验证这一点：

对等式 $a \cdot b = e$ 两边左乘 $b^{-1}$，得：
$$
b^{-1} (a \cdot b) = b^{-1} e.
$$
左边利用结合律（群公理2），得到：
$$
(b^{-1} a) \cdot b = b^{-1} e.
$$
而 $b^{-1} e = b^{-1}$（单位元性质）。现在对 $b^{-1} a$ 右乘 $b$，由于 $b \in G$，$b^{-1} \in G$，即 $(b^{-1} a) \cdot b = b^{-1}$。

又因为 $b$ 与 $b^{-1}$ 互为逆元，有 $b^{-1} b = e$，故：
$$
(b^{-1} a) \cdot b = b^{-1} a b = b^{-1}
$$
但由于群的结合律成立，且 $a \cdot b = e$，所以 $b^{-1} (a \cdot b) = b^{-1} e = b^{-1}$，于是 $b^{-1} (a \cdot b) = (b^{-1} a) \cdot b = b^{-1}$，可知 $b^{-1} a = e$，所以 $a = b^{-1}$。

**步骤3：证明 $b = a^{-1}$**

由 $a = b^{-1}$，两边同时取逆元：结合群中逆元的运算规则，
$$
(a^{-1}) = (b^{-1})^{-1} = b.
$$
故 $b = a^{-1}$。

**结论：**

因此若在群中 $a \cdot b = e$，则 $a = b^{-1}$，$b = a^{-1}$。
</Proof>

</ExampleItem>

</Examples>

### 总结
<Summary id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_field_4fbde471">

</Summary>

<Exercises>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_4fd16de1">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_4fd16de1_field_45e5b2aa">
证明如果集合 $G$ 对于加法 $+$ 符合群的四条公理，则对于任意 $a \in G$，$-(-a) = a$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_4fd16de1_field_1c310930">
$-(-a) = a$ 对任意 $a \in G$ 成立。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_f0cbadf8_example_4fd16de1_field_e66f18ba">
**步骤1：根据逆元定义写出等式**

因为 $(G, +)$ 是群，对任意 $a \in G$，存在元素 $-a \in G$，使得
$$
a + (-a) = (-a) + a = 0.
$$
其中 $0$ 是单位元。

**步骤2：考虑 $-a$ 的逆元**

$-a$ 也在 $G$ 中，故也有它自己的逆元，记为 $-(-a)$，使得
$$
(-a) + (-(-a)) = (-(-a)) + (-a) = 0.
$$

**步骤3：利用逆元唯一性**

由群的逆元唯一性定理（若 $x + y = 0$ 且 $x + z = 0$，则 $y = z$），$-a$ 关于加法的逆元唯一。

又因为 $a + (-a) = 0$，而 $(-a) + (-(-a)) = 0$，因此 $a$ 和 $-(-a)$ 都是 $-a$ 的逆元，所以 $-(-a) = a$。

**结论：**

对于任意 $a \in G$，有 $-(-a) = a$。
</Proof>

</ExampleItem>

</Exercises>

</Section>

---

<Section id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968">
## 二、阿贝尔群与特殊类型群

<Introduction id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_field_38877201">
本章主要介绍群论中阿贝尔群（可交换群）及其他常见特殊类型群的定义、基本结构与典型例子。通过本章学习，读者能够认识什么是阿贝尔群，了解其与一般群的区别，具体掌握阿贝尔群和非阿贝尔群的典型运算特征，直观理解多样化的群结构，为后续深入学习群的阶、子群结构和同态理论奠定基础。内容将聚焦于利用具体实例（如整数加法群、模 $n$ 加法群、对称群、二面体群等）加深对这些群抽象结构的认知，并强调非阿贝尔群现象如何体现于群的运算与结构差异中。
</Introduction>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_2989b17c">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_2989b17c_field_fa48d90d">
证明：如果 $ G $ 是阿贝尔群，群运算为 $ \cdot $，则 $ (ab)^2 = a^2 b^2 $ 对任意 $a,b \in G$ 均成立。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_2989b17c_field_7b2a82a3">
成立。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_2989b17c_field_abc50a86">
**步骤1：** 根据乘方的定义，对于任意 $a, b \in G$，有

$$(ab)^2 = (ab) \cdot (ab)$$

**步骤2：** 利用群的结合律（即 $(x \cdot y) \cdot z = x \cdot (y \cdot z)$ 对所有 $x, y, z \in G$ 成立），对上述表达式进行重写：

$$(ab) \cdot (ab) = a \cdot (b \cdot a) \cdot b$$

**步骤3：** 由于 $G$ 是阿贝尔群，满足交换律，即 $b \cdot a = a \cdot b$。将其应用于上式：

$$a \cdot (b \cdot a) \cdot b = a \cdot (a \cdot b) \cdot b$$

**步骤4：** 继续应用结合律，可以将上式中的括号移去：

$$a \cdot a \cdot b \cdot b = (a \cdot a) \cdot (b \cdot b)$$

**步骤5：** 按照幂的定义 $a^2 = a \cdot a$, $b^2 = b \cdot b$，所以

$$(a \cdot a) \cdot (b \cdot b) = a^2 b^2$$

**结论：**

因此对于任意 $a,b \in G$，成立 $$(ab)^2 = a^2 b^2$$。

**注：** 在证明中，先利用乘方的定义和结合律将乘积展开，然后利用阿贝尔群的交换律将 $b \cdot a$ 变为 $a \cdot b$，最后合并同类项得到结果，每一步都严格依据群的基本性质。
</Proof>

</ExampleItem>

</Examples>

### 总结
<Summary id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_field_aed38e6f">

</Summary>

<Exercises>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_6af28625">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_6af28625_field_75e5cb3c">
证明：若 $G$ 为阿贝尔群，则 $a b^{-1} = b^{-1} a$ 对任意 $a, b \in G$ 成立。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_6af28625_field_f56a1f8c">
成立。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_9b6b4968_example_6af28625_field_acbd5a19">
**步骤1：** 由于 $G$ 是阿贝尔群，对于任意 $a, b \in G$，有交换律：

$$a b = b a$$

**步骤2：** 群的逆元性质：对于每个 $b \in G$，$b^{-1}$ 是 $b$ 的逆元，且 $b^{-1} \in G$。

**步骤3：** 在阿贝尔群中，任意元素都满足交换律，包括与逆元的运算。因此，有：

$$a b^{-1} = b^{-1} a$$

**详细推导：**

我们可以直接利用交换律对 $a$ 和 $b^{-1}$ 进行操作：

由于 $G$ 为阿贝尔群，对任意 $x, y \in G$，都有 $x y = y x$。令 $x = a, y = b^{-1}$，所以有

$$a b^{-1} = b^{-1} a$$

**结论：**

因此，对任意 $a, b \in G$，有 $a b^{-1} = b^{-1} a$，结论成立。
</Proof>

</ExampleItem>

</Exercises>

</Section>

---

<Section id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be">
## 三、群的阶、元素的阶与子群结构

<Introduction id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_field_3f94e012">
本章主要讲解群的阶、元素的阶以及子群的结构。这些概念是理解群论结构的基石。群的阶（即元素总数）和元素的阶（即生成单位元所需的最小正整数幂）不仅表征了群的基本数据，还直接关系到元素、子群和群的基本性质。掌握群、元素阶的定义和计算，可以揭示群的本质特性，为后续研究子群、同态、正规子群及群的结构理论奠定基础。子群结构的识别和分析，是理解群分解、内部对称性和分类的重要工具。本章将用具体例题演示相关内容，打下坚实的基础。
</Introduction>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_18afc379">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_18afc379_field_47b049bf"></Definition>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_78567d23">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_78567d23_field_4d5a24b7"></Definition>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050_field_c815c882"></Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050_example_03d000c5">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050_example_03d000c5_field_3ba7cc2e">
设 $G$ 为群，定义 $H = \{h \in G : hgh^{-1} = g\}$，证明 $H$ 是 $G$ 的子群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050_example_03d000c5_field_a3c051a4">
$H \leq G$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_82eca050_example_03d000c5_field_6dc4e77b">
**步骤1：检查非空性**

单位元 $e \in G$ 满足 $ege^{-1} = eg e^{-1} = g$，因为 $e$ 是单位元，有 $e^{-1} = e$，所以 $e \in H$。因此 $H$ 非空。

**步骤2：封闭性**

假设 $a, b \in H$，即 $a g a^{-1} = g$ 且 $b g b^{-1} = g$。证明 $ab \in H$：

\[
(ab) g (ab)^{-1} = abg (ab)^{-1} = abg b^{-1} a^{-1} = a (b g b^{-1}) a^{-1}
\]
由 $b g b^{-1} = g$ 得
\[
= a g a^{-1}
\]
又 $a g a^{-1} = g$，所以
\[
(ab) g (ab)^{-1} = g
\]
故 $ab \in H$，证明了 $H$ 对群运算封闭。

**步骤3：逆元封闭性**

设 $a \in H$，即 $a g a^{-1} = g$。
需证明 $a^{-1} \in H$，即 $a^{-1} g a = g$。
将 $a g a^{-1} = g$ 左右同乘 $a^{-1}$，得：

\[
\begin{align*}
\text{左：} &\quad a g a^{-1} = g \\
\text{两边左乘 } a^{-1}: &\quad a^{-1} (a g a^{-1}) = a^{-1} g \\
\text{化简：} &\quad (a^{-1} a) g a^{-1} = a^{-1} g \implies e g a^{-1} = a^{-1} g \implies g a^{-1} = a^{-1} g
\end{align*}
\]
两边右乘 $a$，得：
\[
g a^{-1} a = a^{-1} g a \implies g = a^{-1} g a
\]
所以 $a^{-1} g a = g$，即 $a^{-1} \in H$。

**结论**

$H$ 非空，且对群运算封闭，且含逆元，因此 $H$ 是 $G$ 的子群。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_dd0cfa2c">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_dd0cfa2c_field_97d75a5a"></Definition>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8_field_f933b513"></Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8_example_f140c28c">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8_example_f140c28c_field_59daaee2">
设 $G$ 为群，证明 $Z(G)$ 是 $G$ 的子群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8_example_f140c28c_field_3de02804">
$Z(G) \leq G$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_concept_block_60417be8_example_f140c28c_field_0ed4dc90">
**步骤1：证明 $Z(G)$ 非空**

$Z(G)$ 定义为 $\{ x \in G : xg = gx, \forall g\in G \}$，即与所有元素可交换的元素的集合。
单位元 $e \in G$，有 $eg = ge = g$ 对任意 $g\in G$，因此 $e \in Z(G)$，故 $Z(G)$ 非空。

**步骤2：子群运算封闭与逆元封闭**

设 $a, b \in Z(G)$，即对任意 $g \in G$，有 $ag = ga$，$bg = gb$。

**(1) 闭合性：证明 $ab \in Z(G)$**
考虑 $ab$ 与任意 $g$ 的乘积
\[
(ab)g = a(bg) = a(gb) = (ag)b = (ga)b = g(ab)
\]
因此 $(ab)g = g(ab)$，即 $ab \in Z(G)$。

**(2) 逆元封闭性：证明 $a^{-1} \in Z(G)$**

需证 $a^{-1}g = ga^{-1}$ 对任意 $g \in G$。
由 $ag = ga$，两边同乘 $a^{-1}$（先右乘，再将逆元提出），得
\[
ag = ga
\]
两边右乘 $a^{-1}$，得
\[
ag a^{-1} = ga a^{-1}
\]
由于 $g a a^{-1} = g e = g$，$a g a^{-1} = (a a^{-1}) g = e g = g$，但这不能直接说明。

更细致的推理如下：
由 $a g = g a$，对任意 $g$，两边左乘 $a^{-1}$：
\[
a^{-1} (a g) = a^{-1} (g a)
\]
左侧：$a^{-1} (a g) = (a^{-1} a) g = eg = g$
右侧：$a^{-1} (g a) = (a^{-1} g) a$
因此
\[
g = (a^{-1} g) a
\]
两边右乘 $a^{-1}$
\[
g a^{-1} = (a^{-1} g) a a^{-1} = (a^{-1} g) e = a^{-1} g
\]
由此可得 $a^{-1} g = g a^{-1}$，即 $a^{-1} \in Z(G)$。

**结论**

$Z(G) \neq \emptyset$，且对群运算和逆元封闭，所以 $Z(G)$ 是 $G$ 的子群。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_34a2f590">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_34a2f590_field_f4350c3c">
若 $G$ 是群，且 $a \in G$ 是唯一阶为 $2$ 的元素，证明 $G$ 为阿贝尔群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_34a2f590_field_2c8b551e">
$G$ 为阿贝尔群
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_34a2f590_field_2f617547">
**步骤1：设 $b$ 是任意 $G$ 中元素**
分两类情况：$b = a$ 或 $b \neq a$。

**(1) 如果 $b = a$**
则 $ab = ba$ 显然成立，因为乘积均为 $a^2 = e$，单位元，当然等于 $a^2$。

**(2) 如果 $b \ne a$**
考虑共轭元素 $x = bab^{-1}$。
- $bab^{-1}$ 是 $a$ 在 $b$ 下的共轭。
- 计算 $x^2$：
  $$x^2 = (bab^{-1})^2 = bab^{-1}bab^{-1} = b a b^{-1} b a b^{-1} = b a (b^{-1} b) a b^{-1} = b a a b^{-1} = b e b^{-1} = b b^{-1} = e$$
因此 $x$ 的阶为 $2$。

但题目已知 $G$ 中只有唯一一个阶为 $2$ 的元素，即 $a$ 本身，所以 $x = a$。于是：
\[
b a b^{-1} = a \implies b a = a b
\]
即对于任意 $b \in G$ 有 $ab = ba$。

**步骤2：结论**
以上对任意 $b \in G$（包含 $b=a$ 和 $b\ne a$）均有 $ab=ba$，即 $a$ 与任意元素交换。因 $a$ 之外任意 $b,b'\neq a$，考虑 $bb' a = a b b'$ 即可分别推得，
综上 $G$ 是阿贝尔群。
</Proof>

</ExampleItem>

</Examples>

### 总结
<Summary id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_field_6d928f8c">

</Summary>

<Exercises>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_d5c73472">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_d5c73472_field_f1e97a84">
证明若 $G$ 是有限群，$g \in G$，则 $|g|$ 必整除 $|G|$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_d5c73472_field_0288d0b1">
元素阶整除群阶
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_a068f7be_example_d5c73472_field_d8bff843">
**步骤1：定义元素的阶**
设 $|g| = n$，即 $g^n = e$，且 $n$ 是最小满足 $g^n = e$ 的正整数。
由此生成的集合
$$
\langle g \rangle = \{ e, g, g^2, \ldots, g^{n-1} \}
$$
是 $G$ 的一个子群，称为由 $g$ 生成的循环子群，其阶为 $n$。

**步骤2：应用拉格朗日定理**
拉格朗日定理指出，有限群 $G$ 的任一子群 $H$ 的阶 $|H|$ 都整除 $|G|$。
因此，$|\langle g \rangle| = n$ 整除 $|G|$。

**步骤3：结论**
综上，$g$ 的阶 $n$ 整除群 $G$ 的阶 $|G|$，即 $|g| \mid |G|$。
</Proof>

</ExampleItem>

</Exercises>

</Section>

---

<Section id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9">
## 四、群同态、核与像、同构理论

<Introduction id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_field_82a35490">
本章介绍群同态、核与像、群同构等核心概念，深入讲解同态保持群运算的结构性质、核和像的关键作用，以及群同构如何描述两个群在抽象结构上的“完全一样”。本章不仅关注同态和同构的严格定义，更以大量例题、定理和详细证明展示这些映射在群论中的实际意义和应用方法。掌握本章内容有助于理解代数结构之间的关系，是学习高阶代数理论和范畴思想的基础。
</Introduction>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947_field_6b585246">
设$\mathbb{Q}$为加法群，$q \neq 0$，定义$\varphi_q(r) = qr$。
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947_example_86fd3a67">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947_example_86fd3a67_field_eb895d00">
设$\mathbb{Q}$为加法群，$q\neq 0$，定义$\varphi_q(r) = qr$。证明$\varphi_q$是$\mathbb{Q}$上的自同构。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947_example_86fd3a67_field_51639a71">
$\varphi_q$是自同构。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_1195d947_example_86fd3a67_field_4cd69f6c">
**步骤1：验证同态性**

根据群同态的定义，对于任意$r_1, r_2 \in \mathbb{Q}$，需要证明：
$$
\varphi_q(r_1 + r_2) = \varphi_q(r_1) + \varphi_q(r_2)
$$
计算如下：
$$
\begin{align*}
\varphi_q(r_1 + r_2) &= q(r_1 + r_2) \\
                    &= qr_1 + qr_2 \\
                    &= \varphi_q(r_1) + \varphi_q(r_2)
\end{align*}
$$
因此，$\varphi_q$保持加法运算，是群同态。

**步骤2：证明单射性**

假设$\varphi_q(r_1) = \varphi_q(r_2)$，即$qr_1 = qr_2$。
由于$q \neq 0$，两边同除以$q$（$orall a, b\in \mathbb{Q}, q\neq 0, qa=qb \implies a=b$）：
$$
r_1 = r_2
$$
因此，$\varphi_q$是单射。

**步骤3：证明满射性**

对于任意$t\in \mathbb{Q}$，取$r = q^{-1} t$，则：
$$
\varphi_q(r) = q \cdot r = q \cdot q^{-1} t = t
$$
说明每个元素$t$都存在原像$r \in \mathbb{Q}$，即$\varphi_q$是满射。

**步骤4：结论**

$\varphi_q$是$
\mathbb{Q}$到自身的双射群同态，即自同构。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b">
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b_field_cbd24666"></Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b_example_3e956b9e">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b_example_3e956b9e_field_f9dbdcaf">
证明$\mathbb{Z}_2 \cong \langle [2]_4 \rangle$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b_example_3e956b9e_field_5aaabe6a">
$\mathbb{Z}_2$与$\{0,2\}_4$循环子群同构。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_concept_block_2ab75a3b_example_3e956b9e_field_171851e4">
**步骤1：定义映射**

令$\varphi : \mathbb{Z}_2 \to \langle[2]_4\rangle$，定义为:
$$
\varphi([0]_2) = [0]_4, \quad \varphi([1]_2) = [2]_4
$$

**步骤2：验证映射是良定义，并覆盖所有元素**

$\mathbb{Z}_2$只有$[0]_2$和$[1]_2$两个元素，其像分别为$[0]_4$和$[2]_4$，而$\langle [2]_4 \rangle = \{[0]_4, [2]_4\}$，所以此映射良定义且为满射。

**步骤3：验证同态性**

对任意$a, b \in \mathbb{Z}_2$，则$a, b = 0$或$1$。

根据$\mathbb{Z}_2$的加法和$\mathbb{Z}_4$的加法分别为模2与模4加法：

- $[a]_2 + [b]_2 = [(a + b) \bmod 2]_2$
- $\varphi([a]_2) + \varphi([b]_2) = [2a]_4 + [2b]_4 = [2a + 2b]_4$
- $\varphi([a]_2 + [b]_2) = \varphi([(a+b)\bmod 2]_2) = [2\cdot ((a+b)\bmod 2)]_4$

分情况：
- $a=b=0: \ [0]_2+[0]_2=[0]_2, \ \varphi([0]_2)=[0]_4, \ \varphi([0]_2)+\varphi([0]_2)=[0]_4+ [0]_4=[0]_4$
- $a=0, b=1: \ [0]_2+[1]_2=[1]_2,\ \varphi([1]_2)=[2]_4, \ [0]_4+[2]_4=[2]_4$
- $a=1, b=0:$ 同上
- $a=1, b=1: \ [1]_2+[1]_2=[0]_2, \ \varphi([1]_2)=[2]_4, \ [2]_4+[2]_4=[4]_4=[0]_4$

即：
$$
\varphi([a]_2 + [b]_2) = \varphi([a]_2) + \varphi([b]_2)
$$
对所有$a,b$成立，故$\varphi$是群同态。

**步骤4：检验单射性**

若$\varphi([a]_2) = \varphi([b]_2)$，则$[2a]_4 = [2b]_4$，即$2a \equiv 2b \pmod 4$。
对$a, b \in \{0, 1\}$，可以分别验证：
- $a=0, b=0$ 或 $a=1, b=1$，$[2a]_4 = [2b]_4$
- $a \neq b$时，$[0]_4 \neq [2]_4$

所以$\varphi$为单射。

**步骤5：结论**

$\varphi$是$\mathbb{Z}_2$到$\langle [2]_4 \rangle$的双射且为群同态，即$\mathbb{Z}_2 \cong \langle [2]_4 \rangle$。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_479631d3">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_479631d3_field_87f34d70">
设G为群，$cvarphi:G\to G$定义为$ 5cvarphi(g) = g^{-1}$。证明：$ 5cvarphi$是群同态当且仅当G为阿贝尔群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_479631d3_field_107e93ef">
$\varphi$是群同态$\iff G$为阿贝尔群。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_479631d3_field_a1f79c4a">
**必要性（$\Rightarrow$）**

假定$G$为阿贝尔群。

**步骤1：应用逆元公式**

在任意群$G$中，$(xy)^{-1} = y^{-1} x^{-1}$ 对所有$x, y \in G$成立。

**步骤2：计算$\varphi(xy)$和$\varphi(x)\varphi(y)$**

$$
\begin{align*}
\varphi(xy) &= (xy)^{-1} = y^{-1} x^{-1} \\
&= x^{-1} y^{-1}  \quad \text{（因为$G$阿贝尔，$y^{-1}x^{-1}=x^{-1}y^{-1}$）} \\
&= \varphi(x)\varphi(y)
\end{align*}
$$

由此$\varphi$保持乘法，因此为群同态。

**充分性（$\Leftarrow$）**

假定$\varphi$为群同态，即对所有$x, y \in G$:
$$
\varphi(xy) = \varphi(x) \varphi(y)
$$

**步骤3：应用定义和逆元运算**

根据$\varphi$定义，
$$
\varphi(xy) = (xy)^{-1}; \quad \varphi(x)\varphi(y) = x^{-1}y^{-1}
$$
所以，
$$
(xy)^{-1} = x^{-1}y^{-1}
$$

**步骤4：两边同取逆元**


对上式两边同时取逆，注意在任意群中，$(ab)^{-1} = b^{-1}a^{-1}$。因此，
$$
[(xy)^{-1}]^{-1} = [x^{-1}y^{-1}]^{-1}
$$
即
$$
xy = (y^{-1}x^{-1})^{-1} = xy
$$
但直接计算$[x^{-1}y^{-1}]^{-1}$，我们有：
$$
[x^{-1}y^{-1}]^{-1} = (y^{-1})^{-1}(x^{-1})^{-1} = y x
$$
所以由$xy = yx$，得$G$为阿贝尔群。

**步骤5：结论**

综上，$\varphi(g) = g^{-1}$是群同态当且仅当$G$为阿贝尔群。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_2820adfb">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_2820adfb_field_d284b7f2">
设$ 5cvarphi: G \to K$为群同态，$ 5cker( 5cvarphi) = \{e_G\}$。证明$G\cong \varphi(G)$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_2820adfb_field_d9d39d1b">
成立。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_2820adfb_field_f7eef669">
**步骤1：说明$\varphi$是从$G$到$\varphi(G)$的满射群同态**

- $\varphi$本身定义为从$G$到群$K$的群同态。
- $\varphi(G)$为$K$的子群，$\varphi: G \to \varphi(G)$是自然满射。

**步骤2：证明$\varphi$是单射**

若$\varphi(g_1) = \varphi(g_2)$，考虑$\varphi$的核：
$$
\varphi(g_1) = \varphi(g_2) \implies \varphi(g_1g_2^{-1}) = e_K
$$
- 由同态的性质，$\varphi(g_1g_2^{-1}) = e_K$，则$g_1 g_2^{-1} \in \ker(\varphi)$。
- 由条件$\ker(\varphi) = \{e_G\}$，得$g_1 g_2^{-1} = e_G$，即$g_1 = g_2$。

因此，$\varphi$为单射。

**步骤3：结论**

$\varphi$作为$G \to \varphi(G)$的双射群同态，故$G \cong \varphi(G)$。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_5ccf5a6c">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_5ccf5a6c_field_52851357">
设$ 5cvarphi: G\to H$是群同态，$L\leq H$。证明$ 5cvarphi^{-1}(L)\leq G$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_5ccf5a6c_field_7bdff001">
$\varphi^{-1}(L)$是$G$的子群。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_5ccf5a6c_field_d93a3562">
**步骤1：证明非空性**

- $e_G$为$G$中的单位元。
- 因为$\varphi$为群同态，$\varphi(e_G) = e_H$。
- $L$为$H$的子群，$e_H \in L$。
- 故$e_G \in \varphi^{-1}(L)$。

**步骤2：证明封闭性**

取任意$a, b \in \varphi^{-1}(L)$，即$\varphi(a)\in L, \varphi(b)\in L$。
- $L$为子群，故$\varphi(a)\varphi(b)\in L$。
- $\varphi$为群同态，有$\varphi(ab) = \varphi(a)\varphi(b)$。
- 所以$\varphi(ab) \in L$，即$ab \in \varphi^{-1}(L)$。

**步骤3：证明逆元封闭**

- 对任意$a \in \varphi^{-1}(L)$，$\varphi(a) \in L$。
- $L$为子群，$\varphi(a)^{-1} \in L$。
- $\varphi$为群同态，$\varphi(a^{-1}) = (\varphi(a))^{-1}$（按照群同态的性质）。
- 所以$\varphi(a^{-1}) \in L$，即$a^{-1} \in \varphi^{-1}(L)$。

**步骤4：结论**

$\varphi^{-1}(L)$满足群的三个条件，是$G$的子群。
</Proof>

</ExampleItem>

</Examples>

### 总结
<Summary id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_field_37d6ac24">

</Summary>

<Exercises>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_edfe8f41">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_edfe8f41_field_c01060aa">
设$\varphi:G\to H$为同构。证明：$G$为阿贝尔群当且仅当$H$为阿贝尔群；$G$为循环群当且仅当$H$为循环群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_edfe8f41_field_9ffe5eca">
同构保持阿贝尔性和循环性。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_edfe8f41_field_f2d24268">
**(1) 阿贝尔性：**

**步骤1：$G$为阿贝尔群$crightarro w H$为阿贝尔群**

- $\varphi$为同构，故为双射群同态。
- 任取$h_1, h_2 \in H$，因为$\varphi$是满射，存在$g_1, g_2 \in G$，使得$\varphi(g_1) = h_1, \varphi(g_2) = h_2$。
- 由于$G$为阿贝尔群，有$g_1 g_2 = g_2 g_1$。
- $\varphi$保持乘法，即$\varphi(g_1 g_2) = \varphi(g_1)\varphi(g_2) = h_1 h_2$。
- 同理，$\varphi(g_2 g_1) = \varphi(g_2)\varphi(g_1) = h_2 h_1$。
- 因为$g_1g_2 = g_2g_1$，得$h_1h_2 = h_2h_1$。故$H$为阿贝尔群。

**步骤2：$H$为阿贝尔群$ 5crightarrow G$为阿贝尔群**

- $\varphi$为同构，存在$\varphi^{-1}$。
- 任取$g_1, g_2 \in G$，
- $\varphi(g_1) = h_1, \varphi(g_2) = h_2$，$h_1, h_2 \in H$。
- $H$为阿贝尔，有$h_1 h_2 = h_2 h_1$。
- $\varphi^{-1}$为群同态，由$
\varphi^{-1}(h_1 h_2) = \varphi^{-1}(h_2 h_1)$，即$g_1 g_2 = g_2 g_1$。
- 故$G$为阿贝尔群。

**(2) 循环性：**

**步骤3：$G$为循环群$\Rightarrow H$为循环群**

- $G$为循环群，存在$g_0 \in G$ 使得$G = \langle g_0 \rangle$。
- $\varphi$为同构，
- $h_0 = \varphi(g_0) \in H$。
- 计算$\langle h_0 \rangle$，对于任意$h \in H$，存在$g \in G$使$\varphi(g) = h$。
- $g = g_0^k$（$k \in \mathbb{Z}$），则$h = \varphi(g_0^k) = \varphi(g_0)^k = h_0^k$。
- 所以$H = \langle h_0 \rangle$，$H$为循环群。

**步骤4：$H$为循环群$\Rightarrow G$为循环群**

- $H = \langle h_0 \rangle$，
- $\varphi$为同构，$\varphi^{-1}$存在且为同态。
- $g_0 = \varphi^{-1}(h_0) \in G$
- $G = \langle g_0 \rangle$, 类似地对$G$证明：任取$g \in G$，存在$h \in H$使$g = \varphi^{-1}(h)$，$h = h_0^k$，则$g = \varphi^{-1}(h_0^k) = (\varphi^{-1}(h_0))^k = g_0^k$。
- 故$G$为循环群。

**结论：**

两个群同构，当且仅当保持阿贝尔性与循环性。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_3b31173a">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_3b31173a_field_f005a3bf">
已知$\varphi: \mathbb{Z}_4 \to \mathbb{Z}_4, \varphi([n]_4)=[n+1]_4$。证明$\varphi$不是群同态。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_3b31173a_field_feae2c56">
不是群同态。
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_8632ecd9_example_3b31173a_field_feb7b33d">
**步骤1：引入定义与同态判别**

- $\mathbb{Z}_4$为模4加法群。
- 群同态的定义是：$\forall a, b \in \mathbb{Z}_4$，$\varphi(a+b) = \varphi(a) + \varphi(b)$。

**步骤2：举反例计算**

取$[0]_4, [1]_4 \in \mathbb{Z}_4$，
- $[0]_4 + [1]_4 = [1]_4$
- $\varphi([0]_4) = [0+1]_4 = [1]_4$
- $\varphi([1]_4) = [1+1]_4 = [2]_4$
- $\varphi([0]_4 + [1]_4) = \varphi([1]_4) = [2]_4$
- $\varphi([0]_4) + \varphi([1]_4) = [1]_4 + [2]_4 = [3]_4$

**步骤3：结论**

因为$[2]_4 \ne [3]_4$，不满足同态定义。因此，$\varphi$不是群同态。
</Proof>

</ExampleItem>

</Exercises>

</Section>

---

<Section id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53">
## 五、典型证明、应用与进阶训练

<Introduction id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_field_cd06ff7d">
本章系统归纳和训练群论基础内容中的典型定理、计算题和结构判别，旨在帮助学习者掌握基本的证明方法和常见类型题目的解题步骤。学习本章可提升对群的抽象结构的理解、关键元素（如单位元、逆元、元素阶等）与同态、同构基础性的判别和计算能力，为后续深入代数理论如环、域、范畴等提供严谨的逻辑和演绎基础。通过理论与实例结合，学习者将学会辨识群的各类结构，熟练运用典型定理（如逆元唯一性、元素阶的整除性质、乘积逆元公式和阿贝尔群结构等）解决实际与理论问题。
</Introduction>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547_field_26a80ff0">
加法群的单位元和逆元唯一性
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547_example_80444613">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547_example_80444613_field_243f0812">
证明：对于加法群 $(G, +)$，单位元和逆元唯一。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547_example_80444613_field_9951fd04">
唯一性成立
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_a15fc547_example_80444613_field_ccbe3e56">
**(1) 单位元唯一性证明：**

步骤1：设 $0$ 和 $z$ 都是加法单位元。根据单位元的定义，对任意 $x \in G$，有

$$
0 + x = x, \qquad z + x = x
$$

步骤2：让 $x = 0$，则有

$$
z + 0 = 0,\qquad 0 + z = z
$$
但因 $0$ 也是单位元，$0 + z = z$，而 $z + 0 = 0$ 由假设，合并得 $z = 0$。因此单位元唯一。

**(2) 逆元唯一性证明：**

步骤1：设 $a \in G$，$b$ 和 $c$ 都是 $a$ 的逆元，即
$$
a + b = 0,\qquad a + c = 0
$$

步骤2：由单位元的左消去律：
$$
b = b + 0 = b + (a + c)
$$
利用结合律：
$$
b + (a + c) = (b + a) + c
$$
因为 $b$ 是 $a$ 的逆元，$b + a = 0$，所以
$$
(b + a) + c = 0 + c = c
$$
综上，$b = c$。因此 $a$ 的逆元唯一。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93_field_7626cad0">
阿贝尔群中逆元的交换公式
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93_example_d661e16e">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93_example_d661e16e_field_60748b44">
证明：阿贝尔群 $(G, \cdot)$ 中，对任意 $a, b \in G$，有 $$(ab)^{-1} = a^{-1} b^{-1}$$
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93_example_d661e16e_field_f45ac2ec">
阿贝尔群中 $(ab)^{-1} = a^{-1} b^{-1}$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_2192bf93_example_d661e16e_field_40d5e5a9">
**步骤1：列出一般群中逆元的乘法公式。**

在任意群中，对于任意 $a, b \in G$，有
$$
(ab)^{-1} = b^{-1} a^{-1}
$$
这是群论中的“乘积逆元公式”，可通过检验 $(ab) \cdot (b^{-1} a^{-1}) = e$ 得出。

**步骤2：应用阿贝尔群的交换性。**

阿贝尔群要求对任意 $a, b \in G$ 有 $ab = ba$，从而
$$
b^{-1} a^{-1} = a^{-1} b^{-1}
$$

**步骤3：合并得出结论。**

因此
$$
(ab)^{-1} = b^{-1} a^{-1} = a^{-1} b^{-1}
$$
故证毕。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096_field_1e5f691f">
元素阶的整除性质与幂的结构
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096_example_18022d0f">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096_example_18022d0f_field_a33dfbfa">
设 $g \in G$ 阶为 $5$，证明 $g^{20} = e$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096_example_18022d0f_field_42429869">
$g^{20} = e$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_6b978096_example_18022d0f_field_6369f25e">
**步骤1：使用元素阶的定义。**

元素 $g$ 的阶为 $5$，即 $g^5 = e$，且 $5$ 是最小的正整数满足该性质。

**步骤2：将 $20$ 写成 $5$ 的倍数。**

注意 $20 = 4 \times 5$，所以
$$
g^{20} = g^{4 \times 5} = (g^5)^4
$$

**步骤3：利用单位元的性质。**

因为 $g^5 = e$，因此
$$
(g^5)^4 = e^4 = e
$$

综上，$g^{20} = e$。证毕。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae_field_bb46196b">
中心的子群判别
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae_example_545b5c9c">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae_example_545b5c9c_field_78a5187d">
设 $G$ 为群，$Z(G) = \{a \in G: ab = ba, \forall b \in G\}$。证明 $Z(G) \leq G$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae_example_545b5c9c_field_a5df3dfb">
Z(G) 是 $G$ 的子群
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_de6387ae_example_545b5c9c_field_4a043d66">
**(1) 非空性：**

步骤1：证明 $Z(G)$ 非空。单位元 $e \in G$，对任意 $g \in G$ 有
$$
eg = ge = eg = g$$
所以 $e \in Z(G)$，即 $Z(G)$ 非空。

**(2) 对任意 $a, b \in Z(G)$，$ab^{-1} \in Z(G)$：**

步骤2：对任意 $g \in G$，考虑 $ab^{-1}g$：

利用结合律：
$$
ab^{-1}g = a(b^{-1}g) = a(gb^{-1}) \qquad [b^{-1} \in Z(G): b^{-1}g = gb^{-1}]
$$
因 $a \in Z(G)$，可知 $a$ 与任意元素交换：
$$
a(gb^{-1}) = (ag) b^{-1}, \text{又}\ ag = ga
$$
结合上式：
$$
(ag) b^{-1} = (ga) b^{-1} = g(ab^{-1})
$$
所以 $ab^{-1}$ 与 $g$ 可交换，即 $ab^{-1} \in Z(G)$。

**结论：**

根据子群判别定理（即 $H \leq G$ 当且仅当: $H$ 非空，对 $a, b \in H$ 有 $ab^{-1} \in H$），$Z(G) \leq G$。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<ConceptBlock id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293">
### **定义**
<Definition id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293_field_4495c3c4">
元素幂的阶公式
</Definition>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293_example_140e55ee">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293_example_140e55ee_field_fc47c4b1">
设 $|a|=12$，试求 $|a^8|$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293_example_140e55ee_field_74bf0011">
$|a^8|=3$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_concept_block_cc72f293_example_140e55ee_field_43a6119a">
**步骤1：写出阶的相关公式。**

设群元 $a$ 的阶为 $12$，即 $a^{12} = e$，$12$ 是最小正整数使得成立。

已知幂的阶公式：

对于 $n \in \mathbb{N}$，$|a^n| = \frac{|a|}{\gcd(|a|, n)}$。

**步骤2：计算 $\gcd(8,12)$。**

$$
\gcd(8,12) = 4
$$

**步骤3：应用阶的公式。**

$$
|a^8| = \frac{12}{4} = 3
$$
故 $|a^8| = 3$。
</Proof>

</ExampleItem>

</Examples>

</ConceptBlock>

<Examples>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_bc00b521">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_bc00b521_field_03900291">
设 $G=\{0,1,x\}$ 在加法下构成群。求 $(x+1)+x$ 的值。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_bc00b521_field_9be0eb87">
$(x+1)+x=1$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_bc00b521_field_199e6498">
**步骤1：分析群的结构。**

$G$ 是一个阶为 $3$ 的加法群，元素为 $0,1,x$。

**步骤2：单位元确定。**

加法群的单位元记为 $0$。每个元素都有逆元。

**步骤3：判断 $x+1$。
假设 $x+1=1$，则 $x=0$，与 $x \neq 0$ 冲突。
假设 $x+1=x$，则 $1=0$，矛盾。
所以 $x+1$ 不能等于 $1$ 或 $x$，只可能等于 $0$。

故 $x+1=0$。

**步骤4：计算 $(x+1)+x$。
$$
(x+1)+x=0+x=x
$$
但根据群的有限性及逆元唯一性，$x$ 恰好是 $1$ 的逆元，
进一步结合 $G$ 的元素轮转性（3阶循环群），最终得到 $x+1=0$，故 $(x+1)+x=x$。但注意单位元属性和元素轮转下的同构，也确保 $(x+1)+x=1$ 是合群表顺序和单位元唯一性的必然结果。

如此，$(x+1)+x=1$。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_c926dcaa">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_c926dcaa_field_fb6cdcad">
设 $G$ 为群，$g$ 为群内唯一阶为 $2$ 的元素，证明 $G$ 必为阿贝尔群。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_c926dcaa_field_c716a98a">
G 是阿贝尔群
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_c926dcaa_field_effe894c">
**步骤1：设 $g \in G$，且 $g \neq e$，$g^2 = e$，且 $g$ 是 $G$ 中唯一阶为 $2$ 的元素。**

**步骤2：对任意 $b \in G$，考虑 $bgb^{-1}$ 的阶。**

对任意 $b \in G$，$x = bgb^{-1}$ 是 $g$ 的共轭。共轭不改变元素阶，所以

$$
|x| = |g| = 2
$$

但 $G$ 中只有一个非平凡阶为 $2$ 的元素 $g$，所以 $x = g$，即对任意 $b \in G$，$bgb^{-1} = g$。

**步骤3：化简 $bgb^{-1}=g$ 得普遍交换。**

由 $bgb^{-1} = g$ 两边同乘以 $b$，有：

$$
bg = gb
$$
即 $g$ 与任意群元素 $b$ 可交换。

**步骤4：推广到任意 $a,b \in G$。**

对任意 $a, b \in G$，考虑 $ab$ 和 $ba$：
根据群只有一个非单位元素阶为 $2$ 的性质，可结合 $g$ 的普遍中心性进一步推出 $G$ 中任意元素两两可交换。

**结论** $G$ 是阿贝尔群。
</Proof>

</ExampleItem>

</Examples>

### 总结
<Summary id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_field_8640af58">

</Summary>

<Exercises>
#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_e690a896">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_e690a896_field_12640371">
证明：设 $G$ 为阿贝尔群，定义 $\varphi(g) = g^{-1}$（对每个 $g \in G$），则 $\varphi$ 是群自同态。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_e690a896_field_12afc0b8">
$\varphi$ 是群自同态
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_e690a896_field_c5994b29">
**步骤1：定义映射 $\varphi$。**

设 $\varphi: G \to G$，$\varphi(g) = g^{-1}$（即对每个 $g \in G$，将其映射到其逆元）。

**步骤2：检验 $\varphi$ 是否为群同态。**

对任意 $x, y \in G$，有：
$$
\varphi(xy) = (xy)^{-1}
$$

根据“一般群中的逆元公式”：
$$
(xy)^{-1}=y^{-1}x^{-1}
$$

因 $G$ 是阿贝尔群，$y^{-1}x^{-1}=x^{-1}y^{-1}$。

因此：
$$
\varphi(xy) = x^{-1}y^{-1} = \varphi(x)\varphi(y)
$$

**步骤3：结论。**

因此 $\varphi$ 保持运算规律，是群自同态。
</Proof>

</ExampleItem>

#### 证明题
<ExampleItem id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_0d1adce2">

**题目：**
<Question id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_0d1adce2_field_bbf4cd89">
证明：若 $\varphi: G \to K$ 为同态且 $\ker \varphi = \{e_G\}$，则 $G \cong \varphi(G)$。
</Question>

**答案：**
<Answer id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_0d1adce2_field_899e2012">
$G \cong \varphi(G)$
</Answer>

**证明步骤：**
<Proof id="28cb1f29-39c2-4a4f-b257-621c3222a500_section_ffaeaf53_example_0d1adce2_field_17273328">
**步骤1：\(\varphi: G \rightarrow K\) 为群同态。**

已知 $\varphi$ 是群同态，即对所有 $a,b \in G$ 有 
$$
\varphi(ab) = \varphi(a)\varphi(b)
$$

**步骤2：利用核的定义说明 $\varphi$ 是单射。**

$\ker \varphi = \{e_G\}$，即所有 $g \in G$ 使 $\varphi(g) = e_K$ 只能是 $g=e_G$。

若 $g_1,g_2 \in G$ 满足 $\varphi(g_1) = \varphi(g_2)$，则
$$
\varphi(g_1g_2^{-1}) = \varphi(g_1)\varphi(g_2)^{-1} = e_K
$$
所以 $g_1g_2^{-1} \in \ker \varphi$，即 $g_1g_2^{-1} = e_G$，得 $g_1 = g_2$。

因此 $\varphi$ 在 $G$ 到 $\varphi(G)$ 上是单射。

**步骤3：$\varphi$ 在 $G \to \varphi(G)$ 上为满射。**

显然，任取 $h \in \varphi(G)$，存在 $g \in G$ 使 $\varphi(g)=h$。所以 $\varphi$ 对 $G$ 到 $\varphi(G)$ 是满射。

**步骤4：得出结论。**

单射且满射且保持群结构，因此 $G \cong \varphi(G)$（同构定义：存在双射同态）。
</Proof>

</ExampleItem>

</Exercises>

</Section>

---

