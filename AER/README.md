
# Protocolo criado

## Nó quer juntar-se:
    * Calcula o seu ID
    * Envia multicast para a rede com o seu ID, a pedir o sucessor e antecessor
    * "Entra" na rede, passando a atuar como emissor para atualizar as informações
    * Entra efetivamente na rede quando tiver o processo de atualização concluido
    * Ao entrar na rede tem de manter a ligação **sempre** 2 para a frente e 2 para trás
    * Criar os shortcuts -> 2 para a frente, 4 para a frente, 8...


## Nó já existente: 
    * Recebe multicast:
        * Verifica se tem de responder
        * verifica se o ID recebido vai ser o seu sucessor, ou antecessor

    * Recebe unicast:
        * Verifica tipo do pedido:
            * Receptor:
                * Send-content: Envia para o emissor que pediu o conteudo pedido
                * Save-content: Guarda o conteudo enviado pelo emissor
                * Delete-content: Apaga aquilo que foi o emissor pediu para apagar
                * Update-sucessors: Atualiza na sua tabela a informação recebida
                * Update-ancestors: Atualiza na sua tabela a informação recebida

            * Emissor:
                * Send-content: Está a pedir o conteudo X ao receptor
                * Save-content: Está a pedir ao receptor para guardar o conteudo X
                * Delete-content: Está a pedir ao receptor para apagar o conteudo X
                * Update-sucessors: Pede ao receptor para atualizar a sua lista
                * Update-ancestors: Pede ao receptor para atualizar a sua lista