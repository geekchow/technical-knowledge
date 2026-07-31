# Groovy- Difference between List, ArrayList and Object Array

Yes, an Array is a data structure with a fixed size. It is declared as having a type that describes what elements it can hold, that type is covariant (see here for covariant vs contravariant). The Array knows its type at runtime and trying to put anything inappropriate in the Array will result in an exception.

In Groovy, Arrays are not really idiomatic due to being low-level and inflexible (fixed-size). They are supported for interoperation with Java. Typically people using Groovy prefer List over Array. Groovy does try to smooth out the differences, for instance you can use the size method on an Array to get the number of elements (even though in Java you would have to use the length property).

(In Ruby the data structure most closely resembling a list is called Array, so people coming to Groovy or Grails from Rails without a Java background tend to carry over the nomenclature with resulting confusion.)

java.util.List is an interface that describes basic list operations that are implemented by the different kinds of Lists. Lists use generic type parameters to describe what they can hold (with types being optional in Groovy). The generic types on Lists are invariant, not covariant. Generic collections rely on compile-time checking to enforce type safety.

In Groovy when you create a list using the literal syntax (def mylist = []) the java.util.ArrayList is the implementation you get:

```groovy
groovy:000> list = ['a', 'b', 'c']
===> []
groovy:000> list instanceof List
===> true
groovy:000> list.class
===> class java.util.ArrayList
groovy:000> list.class.array
===> false
groovy:000> list << 'd'
===> [d]
groovy:000> list[0]
===> a
```

In order to create an array you have to add as (type)[] to the declaration:

```groovy
groovy:000> stringarray = ['a', 'b', 'c'] as String[]
===> [a, b, c]
groovy:000> stringarray.class
===> class [Ljava.lang.String;
groovy:000> stringarray.class.array
===> true
groovy:000> stringarray << 'd'
ERROR groovy.lang.MissingMethodException:
No signature of method: [Ljava.lang.String;.leftShift() is applicable 
for argument types: (java.lang.String) values: [d]
groovy:000> stringarray[0]
===> a
```

intersect & union compute for list
```groovy
groovy> List<String> listA = ["push", "pop", "append"] 
groovy> List<String> listB = ["count", "list", "size", "append"] 
groovy> // intersect 
groovy> def intersectOfAB = listA.intersect(listB); 
groovy> println intersectOfAB 
groovy> // union 
groovy> def unionOfAB = listA + (listB - intersectOfAB) 
groovy> println unionOfAB 
 
[append]
[push, pop, append, count, list, size]
```

convert array to list
```groovy
groovy> String sentence = "You jump I jump" 
groovy> def splited = sentence.split(" ") 
groovy> println splited 
groovy> println splited.class 
groovy> println splited.toList().class 
 
[You, jump, I, jump]
class [Ljava.lang.String;
class java.util.ArrayList
```

> reference https://stackoverflow.com/questions/28483640/groovy-difference-between-list-arraylist-and-object-array