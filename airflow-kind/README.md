# Airflow with `kind`

To bring up airflow using `kind`:

1. Ensure that the following are available on your system:
    - `docker`
    - `kind`
    - `helm`
    - `kubectl`
2. Change to the airflow-kind directory
    ```console
    $ cd airflow-kind
    ```
3. Make the setup script executable
    ```console
    $ chmod +x up.sh
    ```
4. Run the setup script
    ```console
    $ ./up.sh
    ```

You should now be able to navigate to http://localhost:8080 and find the airflow dashboard.

**The username and password are both "admin"!**

To bring down the service, run:

```console
$ kind delete cluster
```
