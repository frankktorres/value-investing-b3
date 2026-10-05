# 09 — DIÁRIO DE DECISÕES
*Criado em 05/10/2026 (Etapa 1 do `PLANO-DE-MELHORIAS-2026-10.md`, frente F7). Regra de Munger: sem registro da tese, da data e do que provaria o erro, não há aprendizado.*

## Como usar
- Uma entrada por decisão **de compra, venda ou de manter uma posição que estava sob teste** (ex.: acima da saída e mantida). Nunca editar entrada antiga: corrigir com nova entrada que a cita.
- Campos: data · ticker · ação · preço · central/saída da casa na data · tese (3 linhas) · **o que me provaria errado** · data de revisão · execução (preço real, quantidade, imposto — o Frank preenche) · resultado (preenchido na revisão).
- Antes de comprar: passar a lista de vieses do `04` (incentivo, prova social, compromisso, ancoragem no preço pago, disponibilidade de notícia recente).
- Revisão trimestral: classificar cada erro por causa — **dado, método ou viés** — e transformar padrão repetido em mudança de doutrina.
- Preços e centrais são os do hall de 05/10/2026 (fechamento de 02/10, doutrina v2.1); saída = 1,30 × central (§9).

---

## Entradas

### 05/10/2026 — VENDER ITSA4, ABCB4 e RANI3 · MANTER ISAE4
**Contexto.** Recálculo dos 6 lotes (doutrina v2.1). Os três estavam na carteira e acima do preço de saída; ISAE4, também na carteira, abaixo. O Frank delegou a decisão ("decida você"); decidido pela regra de venda do §9 (preço > 1,30 × central), sem exceção de qualidade. **A regra de venda por qualidade (D7 do plano) ainda não existe e não foi usada.**

| Ticker | Ação | Preço 02/10 | Central v2.1 | P/C | Saída 1,30× | Acima da saída |
|---|---|---|---|---|---|---|
| ITSA4 | Vender | R$ 14,67 | R$ 7,11 | 2,06 | R$ 9,24 | +59% |
| ABCB4 | Vender | R$ 26,15 | R$ 13,31 | 1,96 | R$ 17,30 | +51% |
| RANI3 | Vender | R$ 7,94 | R$ 4,87 | 1,63 | R$ 6,34 | +25% |
| ISAE4 | Manter | R$ 28,19 | R$ 24,10 | 1,17 | R$ 31,33 | abaixo (−10%) |

**Tese da venda (comum).** O preço paga mais que o dobro (ITSA4, ABCB4) ou 1,6× (RANI3) o valor que a casa calcula; o retorno esperado de quem compra hoje fica abaixo do Tesouro IPCA+ líquido. Segurar exige acreditar numa premissa que a casa não sustenta.
- **ITSA4:** SOTP R$ 7,33 (Itaú 37,5% ao central de R$ 17,54 por ITUB4) e DDM R$ 6,90; ROE de longo prazo 17,2% contra Ke 19,3%; retorno real implícito 6,4%, abaixo do Tesouro.
- **ABCB4:** Ke implícito 13,3% contra Ke da casa 19,3%; retorno de investimento 13,2%; não vence a renda fixa líquida.
- **RANI3:** ROIC 7,2% abaixo do WACC 15,6% (não cria valor); Ke implícito 14,0%.
- **ISAE4 (manter):** P/C 1,17, abaixo da saída; regulada, DCF regulatório. Pendência: 703 mi de ações (StatusInvest) contra 659 mi na DFP 2025 — com 659 mi seria JUSTA; conferir no RI.

**Destino do dinheiro.** Tesouro IPCA+ 2050; vender no máximo R$ 20 mil por mês de cada papel se houver lucro (isenção de IR em vendas ≤ R$ 20 mil/mês em ações — conferir a regra vigente na doutrina §4.1 antes de executar); se houver prejuízo, a venda não tem esse limite de isenção e o prejuízo compensa ganhos futuros.

**O que me provaria errado** (gatilhos objetivos; qualquer um → reabrir a tese):
- **ITSA4:** o Itaú ser reavaliado para cima do central de R$ 17,54 por evidência de ROE sustentado > 22% (hoje o ROE de longo prazo usado é 17,6%) **ou** a ITSA4 negociar abaixo de R$ 9,24 com o Itaú inalterado (aí a venda terá sido cedo e a recompra, possível).
- **ABCB4:** ROE de 2 anos seguidos acima de 18% com inadimplência 90d < 1% (hoje ROE de longo prazo 12,8%).
- **RANI3:** ROIC acima do WACC por 2 anos seguidos, ou preço de celulose/embalagem que eleve a margem mediana acima de p75 do histórico de forma documentada.
- **Em todos:** o preço cair ≤ 1,30 × central na próxima revisão sem mudança de premissa (a venda teria sido por ruído; a regra, não a decisão, estaria certa — registrar).
- **Custo do erro já conhecido:** vender um negócio bom cedo custa imposto sobre o ganho e o retorno de ficar de fora. Aceito por serem os três de qualidade média e P/C ≥ 1,63.

**Data de revisão:** 05/01/2027 (fecho do 4T26; confere se as três voltaram ao intervalo de compra ou se subiram mais). Revisão extra se a temporada do 3T26 (nov/2026) mudar o central em > 15%.

**Viés a vigiar.** *Ancoragem no preço pago* (não ficar esperando "voltar ao preço médio") e *disponibilidade de notícia recente* (o 1º turno da eleição subiu os preços em 5–11% em 05/10; o central usa 02/10).

**Execução (o Frank preenche):** data · preço real · quantidade · preço médio · lucro/prejuízo · IR devido · Tesouro comprado. *Até a confirmação da venda, a decisão está registrada mas não executada;* ao confirmar, tirar os três da "Carteira" em `PROMPT-AGENTE-NOTICIAS-SEXTA.md` e na cópia de `UPLOAD CLAUDE DESKTOP/`.

**Resultado:** (preencher na revisão).
