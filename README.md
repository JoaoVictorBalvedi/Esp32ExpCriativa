Explicação dos códigos esp32 wokwi.
esp emissora:
primeiro é realizada a conexão com a internet e o broquer hivemq. 
Depois é determinado os pins dos componentes.
Depois o monitoramento de temperatura e umidade é realizado em thread pelas funções "monitorar_sensor1" e "monitorar_sensor2".
Nessas funções ele verifica se a chave está desligada e então verifica se a temperatura é maior que 60 graus para mover os servos, assim como a umidade para enviar o alerta à segunda esp.
a função enviar_alerta é para enviar o alerta à esp receptora pelo broker.

Já na esp32 receptora, a conexão à internet e broker é feita da mesma maneira, mas o código espera uma mensagem por callback e analisa a mensagem.
Se a mensagem contém umidade baixa, ele muda o valor do boolean alarme_ativo, para executar as medidas necessarias, se a mensagem contém umidade noramlizada, ele muda o valor do boolean para parar as ações.
Antes de verificar a mensagem ele verifica se a chave está ligada ou desligada, para prosseguir com o código.
