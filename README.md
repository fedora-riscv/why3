# why3

Why3 is a platform for deductive program verification.  It provides a rich
language for specification and programming, called WhyML, and relies on
external theorem provers, both automated and interactive, to discharge
verification conditions.  (See the
[list of supported provers](http://why3.lri.fr/#provers).)  Why3 comes with a
standard library of logical theories (integer and real arithmetic, Boolean
operations, sets and maps, etc.) and basic programming data structures
(arrays, queues, hash tables, etc.).  A user can write WhyML programs directly
and get correct-by-construction OCaml programs through an automated extraction
mechanism.  WhyML is also used as an intermediate language for the
verification of C, Java, or Ada programs.  (See the list of
[Projects using Why3](http://why3.lri.fr/#users).)  Why3 can be extended
easily with support for new theorem provers.  Why3 can be used as a software
library, through an OCaml API.
