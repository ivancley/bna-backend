#!/usr/bin/env python3
"""
Script para testar o método generate_summary.

Uso:
    python scripts/test_summarize.py

Este script testa diferentes cenários do método generate_summary:
- Texto pequeno
- Texto grande (que será dividido em chunks)
- Texto vazio (fallback para title + description)
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from decouple import config
from api.v1.web_link.ia.summarize import generate_summary

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


TEXTO_PERSONALIZADO = """
Pular para
Pular para o conteúdo
Comentar sobre acessibilidade
Atalhos do teclado
Buscar
/
Minhas compras
P
Carrinho
C
Descrição
D
Questões
Q
Classificações
R
Abrir/fechar o menu de atalhos
Z
Para navegar entre os elementos, use as setas para cima ou para baixo do teclado.
Mercado Livre Brasil - Onde comprar e vender de Tudo
Digite o que você quer encontrar
Buscar produtos, marcas e muito mais…

Ofertas por tempo limitado
Enviar para Ivancley
Rua José Ebaid 2470
Categorias
Ofertas
Cupons
Supermercado
Moda
Mercado PlayGrátis
Vender
Contato
II
IVANCLEY...
Compras
Favoritos
6
3 produtos em seu carrinho3

imagem Apple oficial
Compre produtos novos e certificados

Produto certificado pela Apple em Brasil

Voltar à lista
InformáticaPortáteis e AcessóriosNotebooks
Vender um igual

Compartilhar
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
4
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Acesse a Loja Oficial de Apple


Novo  |  +100 vendidos
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
LOJA OFICIAL APPLE
Vendido por um Revendedor Autorizado Apple.
Produto novo em caixa fechada e com nota fiscal local.
Garantia limitada da Apple por 1 ano.
Garantia AppleCare e serviço de reparo local para produtos fora da garantia.
5.0
Avaliação 5.0 de 5. 20 opiniões.
(20)
Adicionar aos favoritos
Receba cashback nesta compra por ser 
R$
12.499
R$
6.578
,
27
47% OFF
no Pix ou
Saldo no Mercado Pago
ou 
R$
7.739
,
14
 em 21x 
R$
368
,
53
 sem juros com cartão Mercado Pago

Até 
R$
5
 de cashback em Meli Dólar
Ver meios de pagamento e promoções
Cor:Estelar

Estelar
Preto
O que você precisa saber sobre este produto
Processador: Apple M2 Chip M2.
Nome do sistema operacional: macOS.
Capacidade de disco SSD: 256 GB.
Capacidade total do módulo de memória RAM: 16 GB.
Com tela tátil: Não.
Resolução da tela: 2560 px x 1664 px.
Memória unificada mais rápida de até 24 GB para deixar tudo superveloz.
Conjunto de três microfones para capturar sua voz, não os ruídos à sua volta.
Ano de lançamento: 2022.
Ver características
Ir para a compra
Características do produto

Tamanho da tela: 13.6 "


Com tela tátil: Não

Características principais
Marca de placa gráfica integrada
Apple
Capacidade
Capacidade de disco SSD
256 GB
Memória
Capacidade total do módulo de memória RAM
16 GB
Tela
Taxa de atualização da tela
60 Hz
Resolução da tela
2560 px x 1664 px
Com tela tátil
Não
Tamanho da tela
13,6 "
Sistema operacional
Nome do sistema operacional
macOS
Outros
Tipo de produto
Ultrabook
Conectividade
USB
Otimizado para IA
Não
Homologação Anatel Nº
49922201993
Características gerais
Marca
Apple
Linha
MacBook Air
Modelo
A2681
Cor
Estelar
Processador
Marca do processador
Apple
Linha do processador
M2 Chip
Modelo do processador
M2
Quantidade de núcleos
8
Conferir todas as características
Fotos do produto
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado
Apple MacBook Air de 13" Estelar Chip M2 da Apple com CPU de 8 núcleos GPU de 8 núcleos e Neural Engine de 16 núcleos Memória unificada de 16 GB SSD de 256 GB - Distribuidor Autorizado

Ver mais imagens

Descrição
Com a potência do chip M2 de última geração, o novo MacBook Air combina desempenho espetacular e até 18 horas de bateria em uma estrutura de alumínio muito fina*.

• Chip M2 com desempenho de última geração da CPU, GPU e aprendizado de máquina
• CPU de 8 núcleos mais rápida e GPU de até 10 núcleos para executar tarefas complexas2
• Neural Engine de 16 núcleos para tarefas de aprendizado de máquina avançado
• Memória unificada mais rápida de até 24 GB para deixar tudo superveloz
• Até 20% mais rápido para aplicar filtros e efeitos de imagem2
• Até 40% mais rápido para editar timelines de vídeo complexas2
• Até 18 horas de bateria para acompanhar seu dia1
• Design sem ventoinha para você ouvir só o que importa
• Tela Liquid Retina de 13,6 polegadas com 500 nits de brilho e ampla tonalidade de cores P3 para imagens vibrantes e detalhadas3
• Câmera FaceTime HD de 1080p com o dobro de resolução e desempenho em pouca luz
• Conjunto de três microfones para capturar sua voz, não os ruídos à sua volta
• Sistema de som com quatro alto-falantes e Áudio Espacial para uma experiência sonora envolvente
• Compartilhamento de conteúdo entre o iPhone e o Mac
• Porta MagSafe para recarga, duas portas Thunderbolt e entrada para fones de ouvido
• Magic Keyboard retroiluminado com Touch ID para desbloquear o aparelho e fazer pagamentos com segurança
• Conexão sem fio Wi-Fi 6 rápida
• Armazenamento SSD ultrarrápido para abrir apps e arquivos num instante
• macOS Monterey para você se conectar, compartilhar e soltar a criatividade em todos os seus aparelhos Apple
• Disponível em meia-noite, estelar, cinza-espacial e prateado

Itens inclusos: MacBook Air de 13 polegadas, Adaptador de energia USB-C de 30W(chip M2 ou M3 com GPU de 8 núcleos) ou Adaptador de energia USB-C de 35W com duas portas(chip M2 ou M3 com GPU de 10 núcleos e 512 GB de armazenamento), Cabo de USB-C para MagSafe 3(2m).

Avisos legais
Nem todas as configurações estão disponíveis em todos os países. Os dados de desempenho variam de acordo com o modelo e a configuração.
*A duração da bateria varia de acordo com o uso e a configuração.
**Em comparação com a geração anterior.
***A tela do MacBook Air de 13,6 polegadas tem bordas arredondadas na parte superior. Quando medida como um retângulo, a tela tem 13,6 polegadas na diagonal. A área real de visualização é menor.

Aviso legal
• A duração da bateria depende do uso que se dê ao produto.

Ver descrição completa
FRETE GRÁTIS ACIMA DE R$ 19
Receba grátis sexta-feira


Mais detalhes e formas de entrega
Retire grátis a partir de sexta-feira em uma agência Mercado Livre

Comprando dentro dos próximos  56 min 

Ver no mapa
Estoque disponível

Armazenado e enviado pelo
Full

Quantidade:
1 unidade
(+50 disponíveis)

Comprar agora

Adicionar ao carrinho
Adicione e receba grátis os produtos  no seu carrinho.


Loja oficial Apple

+1 M vendas

Devolução grátis. Você tem 30 dias a partir da data de recebimento.
Compra GarantidaVai abrir em uma nova janela, receba o produto que está esperando ou devolvemos o dinheiro.
12 dias de garantia de fábrica.

Adicionar a uma lista

Ir para a loja oficial

Seguir
Loja oficial do Mercado Livre

+50mil Seguidores

+50mil Produtos


MercadoLíder Platinum

É um dos melhores do site!

+1 M

Vendas


Bom atendimento


Entrega no prazo

Ir para a loja oficial
Meios de pagamento
Pague em até 12x sem juros!

Linha de Crédito

Mercado Crédito
Cartões de crédito

Hipercard
Elo
Visa
Mastercard
Pix

Pix
Boleto bancário

Boleto
Confira outros meios de pagamento
Perguntas
Digite sua pergunta...

Perguntar
Ver todas as perguntas
Opiniões do produto
5.0

Avaliação 5.0 de 5. 20 opiniões.
20 avaliações

5
4
3
2
1
Opiniões com fotos
5
Foto do produto compartilhada pelo comprador 1 de 4
5
Foto do produto compartilhada pelo comprador 2 de 4
5
Foto do produto compartilhada pelo comprador 3 de 4
5
Foto do produto compartilhada pelo comprador 4 de 4

Ordenar

Qualificação
Opiniões em destaque
7 comentários
Avaliação 5 de 5
07 out. 2025
Foto do produto compartilhada pelo comprador 1 de 1
Perfeito, veio na caixa lacrado. Ameiii.


É útil
5

Mais opções
Avaliação 5 de 5
02 out. 2025
Foto do produto compartilhada pelo comprador 1 de 1

É útil
4

Mais opções
Avaliação 5 de 5
04 out. 2025
Foto do produto compartilhada pelo comprador 1 de 1
Estou muito feliz!.


É útil
3

Mais opções
Avaliação 5 de 5
13 out. 2025
Foto do produto compartilhada pelo comprador 1 de 2
Foto do produto compartilhada pelo comprador 2 de 2

É útil
1

Mais opções
Avaliação 5 de 5
04 out. 2025
Estou gostando muito! vale.


É útil
1

Mais opções
Mostrar todas as opiniões
Anúncio #5417757006

DenunciarVai abrir em uma nova janela
Destaques em Informática
Tablet
Tab 15 pro
Ipad
Tablet samsung
Ipad 9
Tablet xiaomi
Ipad 10
Ipad pro
Ver tudo
Placa de Vídeo
Gtx 1080 ti
Gtx 1650
Rtx 2060
Rtx 2070
Rtx 3060
Rtx 3060 ti
Rtx 3080
Ver tudo
Pc
Pc gamer
Workstation hp z8
Pc trabalho
Cpu
Notebook
Notebook dell
Notebook gamer
Macbook air m2
Macbook air m1
Notebook samsung
Macbook
Netbook
Ver tudo
Mais informações
Copyright © 1999-2025 Ebazar.com.br LTDA.
Trabalhe conosco
Termos e condições
Promoções
Como cuidamos da sua privacidade
Acessibilidade
Contato
Informações sobre seguros
Programa de Afiliados
Lista de presentes
CNPJ n.º 03.007.331/0001-41 / Av. das Nações Unidas, nº 3.003, Bonfim, Osasco/SP - CEP 06233-903 - empresa do grupo Mercado Livre.

Mercado Livre
"""


def test_custom_text():
    """Permite testar com texto personalizado."""
    print("\n" + "="*80)
    print("🎯 TESTE COM TEXTO PERSONALIZADO")
    print("="*80)
    
    # Você pode modificar este texto para seus testes
    
    
    try:
        api_key = config("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        print(f"Tamanho do texto personalizado: {len(TEXTO_PERSONALIZADO)} caracteres")
        
        summary = generate_summary(
            client=client,
            title="Teste Personalizado",
            text_full=TEXTO_PERSONALIZADO,
            description="Resumo de teste personalizado"
        )
        
        print("\n📋 RESUMO GERADO:")
        print("-" * 40)
        print(summary)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Erro no teste personalizado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do generate_summary...")
    
    # Executar testes principais
    # test_generate_summary()
    
    # Executar teste personalizado
    test_custom_text()
    
    print("\n🎉 Testes finalizados!")