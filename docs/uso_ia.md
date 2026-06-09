# Uso de Inteligência Artificial — Global Solution 2026/1

## Ferramentas utilizadas

- **Claude (Anthropic)** — assistente de IA utilizado como apoio ao longo do desenvolvimento.

## Em quais partes a IA foi utilizada

A IA foi utilizada como ferramenta de apoio para:

- Organizar e revisar ideias durante o planejamento do sistema
- Apoiar a redação e formatação do README e da documentação
- Tirar dúvidas pontuais sobre conceitos abordados nas fases do curso

## O que a equipe desenvolveu diretamente

- Toda a lógica do sistema (`src/sistema.py`): estruturas de dados, regras booleanas, geração de alertas, regressão linear e menu interativo
- Os dados simulados e a lógica do gerador (`src/gerador.py`)
- As decisões de design: quais módulos monitorar, quais limiares usar, como priorizar alertas
- A análise e interpretação dos resultados gerados pelo sistema


## Validação crítica realizada

- Cada sugestão da IA foi lida, compreendida e testada antes de aplicada
- O sistema foi executado manualmente em cada etapa do projeto, garantindo integridade e consistência
- As regras booleanas e a regressão linear foram revisadas pela equipe para confirmar que refletem cenários operacionais reais e coerentes
