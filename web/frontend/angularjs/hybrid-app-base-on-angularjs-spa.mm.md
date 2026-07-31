# A hybrid mobile application base on angularjs

## Optimization

### Lazy loading 
loading when route state is activated.
  
#### module
#### language resources

### Internalization
#### Language resource partially loading

### Decorator

  - Component
  - Directive
  - Service

### Obfuscation

  - webpack-obfuscation
  - babel-plugin-class-name

## UI Interaction

### SCSS/SASS
organizable/reusable/standarised css components

### Directive 

#### Common components

  - input
  - validator
  - ...

### Animation
  - page transistion
  - element show/hiden
  - animation basic 
    - fade
      - fade in 
      - fade out
    - move 
      - left
      - right
      - up
      - down
    - timing function
      - ease in/out
      - cubic function

### Gesture
  - [hammerjs](https://hammerjs.github.io/)

### Accessibility
  - aria
    - aria-label
    - aria-hiden
    - aria-controls
    - aria-expanded
    - aria-describedby
  - tab-index
    - 0
    - 1
    - -1
  - role
    - button
    - alert
    - text-box

## Fundalmentals
  - api fetcher
    - unified message handling
    - unified error handling
  - different env support
    - dummy
    - alpha 
    - belta
    - prod
  - webpack
    - live-reload
    - uglify
    - obfuscate
  - a proxy to pass request to backend when debugging in browser
  - dummy mode
  - postman script


## Operation Support

### Tagging
  - Tealium SDK 
    - Wrapped with cordova plugins
    - Tag management system
      - google analysis
      - adobe
      - webtrend

### Logging
  - AppDynamic

## Disadvantage

### Webview comptiable
  - animation render issue
  - option input cannot click: css hack
  - quick double click no response: fastclick
  - input with keyboard
    - webview is pushed up
    - header cannot be fixed
    - keyboard plugins to lock the webview

### Javascript
  - performance issue
    - long bootstrap time
    - long list rendering
  - no compiling error checking
  - navigation cache: every navigation need rerender
  - js executed background
    - needs to put Webview into UIWindow otherwise js won't execute or ui won't update.

## Advantage
  - hot update
    firefight 
  - one code base
  - customized ui
  - live reload(dev)
