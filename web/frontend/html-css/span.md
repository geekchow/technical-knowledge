# html element span

`span` is an inline element, which means, it has not height and width.
The size depends on the elements within it.

So you're not able to specify `width` or `height` for it.
However, sometimes we do need to set width & height for it.
Then, we can use property: `display: inline-block`, to convert it.

There is a typical use case.
Align a SVG with a span within a un-order list item.

```html
<!DOCTYPE html>
<html>
    <style>
        .tick-item {
          display: inline-block;
          /* set the vertical-aling to super */
          /* vertical-align: super; */
        }
    </style>
    <body>
        <div id="tick-icon">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>
            <span class="tick-item">checked passed</span>
          </div>
    </body>
</html>
```

Even through the span is inline-block now. But the default vertical-align value is `baseline`. So text is lower than svg icon. We can adjust the `vertical-align` property to align text with svg.