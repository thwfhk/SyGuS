# Program Synthesis

软分分析Project 2报告

组员：唐雯豪 易普 谢睿峰

## 运行

在根目录下执行`python src/wrapper.py test/open_test/filename.sl`进行测试.

需要Racket和Rosette支持：
* 在 https://download.racket-lang.org 下载安装racket，并添加环境变量到shell
* 运行`raco pkg install rosette`安装Rosette

需要再linux系统下运行（因为将Haskell相关内容编译成了一个linux下的exe）

注意：该程序可以在时间限制下解出`open_tests`中的所有样例，如果有报错等情况发生，请联系我们🥺。

## 方法

我们组实现了四种方法，最后的方案是将三种方法拼接在一起。

可以解出`open_tests`里的全部问题，并且在大部分问题上速度极快。

### VSA-based

代码在`src/vsa-based`目录。

我们听信了熊老师说的“FlashMeta非常快，当前最快的程序综合算法MaxFlash就是基于FlashMeta”之后就写了一个基于VSA的程序综合算法，基本过程上课讲的与FlashMeta论文中一样。

结果只能解出`three.sl`和`max2.sl`，被骗了:(

沉没成本，果断放弃。

### 直接法（乱来法）

> 他说他是乱打的。他可不是乱打的啊，看来是有备而来。

代码在`src/direct`目录。

这是我们的主要方法，可以解出`array_search`系列所有问题, `s1.sl`, `s2.sl`, `s3.sl`, `tutorial.sl`。并且速度极快，可以在1s之内解出，~~宛如打表~~。

该方法**直接从约束中综合出程序**，理论上对于所有SyGuS问题，只要它对函数结果的约束只有等号约束，并且函数结果只在等号一边出现，都可以用该方法解出。
所以该方法无法解决`max`系列问题（因为对函数结果有不等号约束），也无法解决`three`问题（因为约束中有一条函数结果在两边出现了，这实际上是个递归，但是给的语法又不支持不动点组合子，所以解不了）

具体算法分为三个步骤：
1. 约束规范化
2. 分支提取
3. 局部搜索，解语法糖

具体三个步骤的描述我们会在作报告的时候详细描述，报告slides可以在[github repo](https://github.com/thwfhk/SyGuS)上找到。

### 新DSL+搜索

代码在`src/search`目录。

这个方法主要用来解决`max`系列问题。

吉老师曾经说过，“目前 Synthesis 方法的效率高度依赖 DSL 的设计”。所以我们引入了一个新DSL语法：`(max x y) = (ite (< x y) y x)`，利用这个语法可以非常快的搜出`max`系列问题，只要在最后加一个解语法糖就可以了。与之类似，对`min`的支持也可以通过引入一个语法糖来解决。

需要注意的是，给出的文法如果不够强，就无法用上述方法表示`max`或`min`，因此需要最终结果中输出的函数必须和给出的文法中具有哪些运算符相适应。

这部分代码使用了Haskell实现，~~可谓徒手造轮子，~~遭遇了包括但不限于SBV、`haskell-z3`等的一系列奇奇怪怪的bug。最终的程序采用命令行调用`z3`的方式和SMT Solver交互，所以需要`z3`在PATH中才能正确运行。

### Rosette

代码在`src/rosette`目录。

Rosette是Racket的一个库，提供了solver-aided programming，将代码与SMT solver更好的整合在一起。

Rosette中提供了一个`define-sythax`，可以定义一个CFG语法并展开k层，然后进行程序综合。并且使用了一种算法来合并相同的符号表达式提高效率。

我们将基于Rosette实现的程序综合方法作为“直接法”和“新DSL+搜索”都解不出来的时候的最后方法。
