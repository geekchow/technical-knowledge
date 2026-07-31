## Difference Between `ping` and `telnet`

- **`ping`**  
  - Used to check if a host (IP address or domain) is reachable on the network.
  - Uses ICMP protocol (not TCP/UDP).
  - **Cannot specify a port**—it only checks if the host is alive, not if a specific service/port is open.

- **`telnet`**  
  - Used to test connectivity to a specific IP address **and port**.
  - Uses TCP protocol.
  - Useful for checking if a service (like Redis on port 6379) is reachable.

### Examples

- Check if host is reachable:
  ```sh
  ping 133.0.195.91
  ```

- Check if port 6379 is open:
  ```sh
  telnet 133.0.195.91 6379
  ```

- Or using `nc` (netcat), which is often preferred for port checks:
  ```sh
  nc -vz 133.0.195.91 6379
  ```

**Summary:**  
- Use `ping` to check if a host is up.
- Use `telnet` or `nc` to check if a specific port is open.