# svision server

<div align="center">
  <img src="../assets/images/svision.png"><br><br>
</div> 

-----------------

## Configuração do ambiente

- Instalar o anaconda
- Criar um ambiente virtual python
    - ```conda create --name svision python=3```
    - ```conda activate svision```



## Utilidades

-> encerra o bind da porta ```lsof -i :5000```

-----------------

## Docker

* Suporte incluido baseado neste [link](http://www.easy-analysis.com/dockerizing-python-flask-app-and-conda-environment/).

```$ docker build -t svision:1.0 .```
### Para rodar
```$ docker run --name svision -p 5001:5000 --rm svision:1.0```
### Para acessar
```localhost:5001```

