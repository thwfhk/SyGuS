# Program Synthesis

软分分析Project 2报告

组员：唐雯豪 易普 谢睿峰

## 运行

在根目录下执行`python src/wrapper.py test/open_test/filename.sl`进行测试.

需要Racket和Rosette支持：
* 在 https://download.racket-lang.org 下载安装racket，并添加环境变量到shell
* 运行`raco pkg install rosette`安装Rosette

需要在linux系统下运行（因为将Haskell相关内容编译成了一个linux下的exe）

注意：该程序可以在时间限制下解出`open_tests`中的所有样例，如果有报错等情况发生，请联系我们🥺。

## 提交的样例
文件是`test/min15.sl`。

## 方法

我们组实现了四种方法：
* VSA `src/vsa-based`
* 直接法 `src/direct`
* DSL增强的搜索 `src/search`
* 基于Rosette的暴力展开 `src/rosette`


最后的方案是并行跑“直接法”和“DSL增强的搜索”。

可以解出`open_tests`里的全部问题，并且在大部分问题上速度极快。

**四种方法的具体描述见`slides.pdf`**