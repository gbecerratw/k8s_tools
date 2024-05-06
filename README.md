# K8S Tools

Tools for k8s clusters health analysis. It is recommended to use a venv tool, for simplicity you can use [Anaconda](https://www.anaconda.com/download) and create a new environment.

1. After install Anaconda create a new python environment, don't forget to select/activate the right env inside VS Code.

    ```
    conda create -n k8s_tools python=3
    ```

2. Install the requirements

    ```
    pip install -r requirements.txt
    ```

3. To use the orphan HPA script please pass the namespace as a parameter

    ```
    python hpas.py --ns=here-goes-your-namespace
    ```