# Certificate pinning

When developing a mobile application, especially financial apps. Security is a must to be taken into consideration. 
Then, how can we proceted our data through the internet, between client and server. You may say we have Https which 
could protect our data transfrom on the internet. But is it really safety?  There are several scenarios https fails to 
protect you.

1. Certificate Authority is hijacked. 
2. A Man in the Middle attack. 

Under those scenarios, the basic https secure mechanism doesn't work anymore. 
We need to verify the certificate from server by ourselves.
Store the public key or hash of the key on the app. And let the code to verify 
if the certificate return from server is matched with local hash or certificate.

