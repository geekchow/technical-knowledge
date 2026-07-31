# Jenkins Tips

## where does jenkins.util.SystemProperties read config from ?

`Jenkins.util.SystemProperties` reads configuration values from system properties in the Java Virtual Machine (JVM). These properties are typically set using the `-D` command line option when launching the JVM, for example: `java -Dproperty.name=property.value`. The SystemProperties class provides a convenient way to access these properties from within the Jenkins codebase.

> implementation 

```java
package jenkins.util;

public final class SystemProperties {
  private SystemProperties() {}

  public static String getString(String key) {
    return System.getProperty(key);
  }

  public static String getString(String key, String defaultValue) {
    return System.getProperty(key, defaultValue);
  }

  public static int getInteger(String key, int defaultValue) {
    String value = System.getProperty(key);
    if (value == null) {
      return defaultValue;
    }
    try {
      return Integer.parseInt(value);
    } catch (NumberFormatException e) {
      return defaultValue;
    }
  }

  public static boolean getBoolean(String key, boolean defaultValue) {
    String value = System.getProperty(key);
    if (value == null) {
      return defaultValue;
    }
    return Boolean.parseBoolean(value);
  }
}

```

So actually, it's a wrapper class of `System.getProperty`. 

The System.getProperty method is a static method in the java.lang.System class that returns the value of a system property. System properties are key-value pairs that are set at the JVM level and can be used to configure the behavior of the JVM and the applications running on it.

Here's an example of how you might use System.getProperty to get the value of the user.home system property:

```java
String userHome = System.getProperty("user.home");
System.out.println("User home directory: " + userHome);

```

```shell
java -Dmy.custom.property=my.custom.value MyMainClass
```

This sets the my.custom.property system property to `"my.custom.value"`, which can be retrieved from within your Java code using `System.getProperty("my.custom.property")`.

