# Projeto-Microcontroladores-Orquestra
##Orquestra Eletrônica
### Visão Geral
Este projeto consiste em criar uma “orquestra eletrônica”,  utilizando diferentes dispositivos comuns, como máquina de costura, impressora, liquidificador e drive de CD. O objetivo é transformar aparelhos domésticos em instrumentos musicais controlando os motores DC. 

###Componentes Utilizados
●	Arduino Mega.
●	Motor Shield:
●	Motores DC: Responsáveis por acionar os dispositivos,
1.	Mini Liquidificador 
2.	Escova elétrica
3.	Impressora 
4.	Drive de CD
5.	Máquina de costura de mão 

●	Ponte H: Utilizada especificamente para controlar o motor do liquidificador devido à sua alta demanda de corrente. A Ponte H é utilizada para assegurar que o motor do liquidificador receba a corrente adequada, evitando sobrecargas e garantindo a integridade do sistema.
●	Fontes de Alimentação:
○	Fonte 1: 9V para alimentar os motores da impressora, drive de CD, máquina de costura de mão, escova elétrica.
○	Fonte 2: 6V em corrente alternada (AC) para alimentar o mini liquidificador.

###Divisão de Instrumentos: Os instrumentos são divididos em dois grupos principais:
○	Percussão: Escova elétrica e mini liquidificador. 
○	Batida: Impressora, drive de CD e máquina de costura produzem sons de batida.
Utilização
●	Piano Virtual: Um piano virtual é utilizado para criar melodias, onde cada tecla corresponde a uma nota musical (Do, Ré, Mi, Fá, etc.).
●	Envio de Comandos: A melodia criada no piano virtual, junto com as seleções de batidas, é enviada via comunicação serial para o Arduino.
●	Controle dos Motores: O Arduino recebe os comandos e aciona os motores correspondentes de acordo com as notas e ritmos programados.
Desenvolvimento e Testes
Durante um período de 1 mês, diversos dispositivos foram testados para integrar a orquestra. Após os testes, os dispositivos selecionados foram mapeados para corresponder às notas musicais, garantindo que cada um produza um som que se assemelhe às notas tradicionais.



