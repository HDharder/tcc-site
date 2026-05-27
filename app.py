import streamlit as st
import random
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Criptografia Híbrida V4", layout="wide")

# --- MATEMÁTICA DO RSA (ALGORITMOS AVANÇADOS) ---
def miller_rabin(n, k=5):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
        
    for _ in range(k):
        a = random.randint(2, n - 2) if n > 3 else 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1: return None
    return x % phi

def get_valid_key_pairs(phi):
    pairs = []
    test_es = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 257, 65537]
    for e in test_es:
        if e < phi and math.gcd(e, phi) == 1:
            d = mod_inverse(e, phi)
            if d and d != e: 
                pairs.append({"Chave Pública (E)": e, "Chave Privada (D)": d})
                
    if len(pairs) < 5:
        for e in range(3, min(phi, 2000), 2):
            if math.gcd(e, phi) == 1:
                d = mod_inverse(e, phi)
                if d and d != e and {"Chave Pública (E)": e, "Chave Privada (D)": d} not in pairs:
                    pairs.append({"Chave Pública (E)": e, "Chave Privada (D)": d})
                if len(pairs) >= 8: break
    return pairs

def rsa_encrypt(m, e, n): return pow(m, e, n)
def rsa_decrypt(c, d, n): return pow(c, d, n)


# --- MATEMÁTICA DO MOTOR CAÓTICO (AGORA RETORNA OS BASTIDORES DA FÓRMULA!) ---
def logistic_map_sequence(seed, length):
    x = seed
    bit_stream = []
    math_details = [] # Guarda o histórico da fórmula para exibição
    
    for _ in range(length):
        x_prev = x
        x = 4 * x_prev * (1 - x_prev)  # A fórmula do Caos executada
        bit = 1 if x >= 0.5 else 0      # O Limiar / Arredondamento
        
        bit_stream.append(bit)
        math_details.append((x_prev, x, bit))
        
    return bit_stream, math_details

def bytes_to_bits(byte_data):
    bits = []
    for b in byte_data:
        bits.extend([int(bit) for bit in format(b, '08b')])
    return bits

def bits_to_bytes(bits):
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte_chunk = bits[i:i+8]
        if len(byte_chunk) < 8: break
        bytes_list.append(int("".join(str(b) for b in byte_chunk), 2))
    return bytes(bytes_list)


# --- INICIALIZAÇÃO DA MEMÓRIA GLOBAL ---
if 'P' not in st.session_state: st.session_state.P = 317
if 'Q' not in st.session_state: st.session_state.Q = 331
if 'N' not in st.session_state: st.session_state.N = 104927
if 'E' not in st.session_state: st.session_state.E = 17
if 'D' not in st.session_state: st.session_state.D = 49073

if 'original_seed' not in st.session_state: st.session_state.original_seed = None
if 'encrypted_seed' not in st.session_state: st.session_state.encrypted_seed = None
if 'historico_caos' not in st.session_state: st.session_state.historico_caos = []


# --- BARRA LATERAL (MENU ESQUERDO) ---
st.sidebar.header("⚙️ Painel Híbrido")

modo = st.sidebar.radio(
    "Como ler a mensagem?", 
    ("Codificar (Texto ➔ Hex)", "Decodificar (Hex ➔ Texto)"),
    help="Define se o texto digitado é claro ou se já é o lixo digital em Hexadecimal."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Tranca RSA da Semente")

seed_input = st.sidebar.number_input(
    "Semente Caótica (X₀):", 
    min_value=0.00001, max_value=0.99999, value=0.12345, step=0.00001, format="%.5f"
)

if st.sidebar.button("🔐 Cifrar Semente via RSA"):
    seed_int = int(round(seed_input * 100000))
    st.session_state.encrypted_seed = rsa_encrypt(seed_int, st.session_state.E, st.session_state.N)
    st.session_state.original_seed = seed_input
    st.sidebar.success("Semente salva e cifrada no plano de fundo!")

if st.session_state.original_seed is not None:
    st.sidebar.info(f"Semente em uso: **{st.session_state.original_seed}**")
    st.sidebar.warning(f"Semente Cifrada (RSA): **{st.session_state.encrypted_seed}**")


# --- ÁREA PRINCIPAL DO SIMULADOR ---
st.title("🛡️ Sistema de Criptografia Híbrida")

tab_principal, tab_caos, tab_rsa = st.tabs(["🚀 Terminal Principal", "🔬 Análise Matemática do Caos", "🧮 Laboratório do RSA"])

# ABA 1: TERMINAL PRINCIPAL
with tab_principal:
    st.markdown("<style>textarea {resize: none !important;}</style>", unsafe_allow_html=True)
    mensagem_input = st.text_area("Insira sua mensagem aqui:", value="Olá, munDo! 🚀", height=150)
    
    if st.button("Executar Sistema"):
        if st.session_state.original_seed is None:
            st.error("Por favor, cifre a semente na barra lateral primeiro!")
        else:
            if modo == "Codificar (Texto ➔ Hex)":
                bytes_msg = mensagem_input.encode('utf-8')
                bits_msg = bytes_to_bits(bytes_msg)
                
                # Agora recebemos os bits E os detalhes matemáticos de cada iteração
                caos_bits, caos_details = logistic_map_sequence(st.session_state.original_seed, len(bits_msg))
                
                bits_cifrados = [m ^ c for m, c in zip(bits_msg, caos_bits)]
                hex_final = bits_to_bytes(bits_cifrados).hex().upper()
                
                st.success("Codificação concluída com sucesso!")
                st.info(f"**Resultado Hexadecimal:**\n\n`{hex_final}`")
                
                # CONSTRUÇÃO DO HISTÓRICO COM TABELA DE MATEMÁTICA
                st.session_state.historico_caos = []
                idx = 0
                for char in mensagem_input:
                    char_bytes = char.encode('utf-8')
                    tamanho_bits = len(char_bytes) * 8
                    
                    char_bits = bits_msg[idx:idx+tamanho_bits]
                    char_caos_bits = caos_bits[idx:idx+tamanho_bits]
                    char_cifrado = bits_cifrados[idx:idx+tamanho_bits]
                    char_hex = bits_to_bytes(char_cifrado).hex().upper()
                    
                    # Constrói a tabela em Markdown da fórmula matemática para a letra
                    tabela_markdown = "\n| Passo | Entrada ($X_n$) | Cálculo: $4 \\times X_n \\times (1 - X_n)$ | Limiar ($>= 0.5$) | Bit |\n"
                    tabela_markdown += "|:---:|:---:|:---|:---:|:---:|\n"
                    
                    detalhes_fatia = caos_details[idx:idx+tamanho_bits]
                    for j, (x_prev, x_next, bit_val) in enumerate(detalhes_fatia):
                        # Define visualmente a avaliação
                        limiar = "🟩 Sim" if bit_val == 1 else "🟥 Não"
                        tabela_markdown += f"| {j+1} | {x_prev:.6f} | {x_next:.6f} | {limiar} | **{bit_val}** |\n"
                    
                    # Junta as informações da letra com a tabela
                    st.session_state.historico_caos.append(
                        f"### 🔠 Caractere: '{char}' (Bytes: {len(char_bytes)})\n"
                        f"> **Bits Originais:** `{char_bits}`\n>\n"
                        f"> **Bits do Caos:** `{char_caos_bits}`\n>\n"
                        f"> **Bits Cifrados:** `{char_cifrado}` ➔ **HEX:** `{char_hex}`\n\n"
                        f"**Evolução da Órbita Caótica para gerar os bits acima:**\n"
                        f"{tabela_markdown}\n"
                        "---"
                    )
                    idx += tamanho_bits

            elif modo == "Decodificar (Hex ➔ Texto)":
                try:
                    bytes_cifrados = bytes.fromhex(mensagem_input)
                    bits_cifrados = bytes_to_bits(bytes_cifrados)
                    
                    caos_bits, _ = logistic_map_sequence(st.session_state.original_seed, len(bits_cifrados))
                    
                    bits_originais = [c ^ ch for c, ch in zip(bits_cifrados, caos_bits)]
                    texto_recuperado = bits_to_bytes(bits_originais).decode('utf-8')
                    
                    st.success("Decodificação concluída com sucesso!")
                    st.info(f"**Mensagem Original Recuperada:**\n\n{texto_recuperado}")
                    st.session_state.historico_caos = ["*A análise matemática detalhada foi gerada durante a codificação. Para ver a matemática abrindo passo a passo, codifique uma nova mensagem primeiro.*"]
                except Exception as e:
                    st.error("Erro na decodificação. Verifique se o Hexadecimal é válido!")

# ABA 2: ANÁLISE PASSO A PASSO (AGORA COM TABELAS IMERSIVAS)
with tab_caos:
    st.header("🔬 Análise Matemática do Motor Caótico")
    st.write("Abaixo acompanhamos cada iteração da fórmula do **Mapa Logístico**. Veja exatamente como os valores orbitam caoticamente e como o sistema define se aquele pulso vale 0 ou 1.")
    
    if st.session_state.historico_caos:
        for linha in st.session_state.historico_caos:
            st.markdown(linha)
    else:
        st.write("Execute a **Codificação** na aba Principal para gerar a tabela matemática.")

# ABA 3: MATEMÁTICA DO RSA (TOTALMENTE MODIFICADA CONFORME PEDIDO)
with tab_rsa:
    st.header("🧮 Laboratório de Teoria dos Números (RSA Dinâmico)")
    st.write("Configure as chaves e explore os fundamentos matemáticos e algoritmos envolvidos.")
    
    # Colunas para organizar a entrada de P e Q e o painel de chaves
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Geração de Primos")
        p_input = st.number_input("Escolha o número primo P:", value=int(st.session_state.P), step=1)
        q_input = st.number_input("Escolha o número primo Q:", value=int(st.session_state.Q), step=1)
        
        # Requisito 1: Validação obrigatória via Miller-Rabin antes de salvar
        if st.button("Validar e Aplicar Primos"):
            p_valido = miller_rabin(p_input)
            q_valido = miller_rabin(q_input)
            
            if not p_valido:
                st.error(f"❌ O valor P={p_input} FALHOU no teste de Miller-Rabin! Não é um número primo.")
            if not q_valido:
                st.error(f"❌ O valor Q={q_input} FALHOU no teste de Miller-Rabin! Não é um número primo.")
                
            if p_valido and q_valido:
                st.session_state.P = p_input
                st.session_state.Q = q_input
                st.session_state.N = p_input * q_input
                st.success("✅ Ambos os números passaram no teste de Miller-Rabin e foram aplicados!")
                st.rerun()

        # Requisito 3: Explicações teóricas expansíveis integradas
        with st.expander("📚 Como funciona o Teste de Miller-Rabin?"):
            st.write("""
            O teste de **Miller-Rabin** é um algoritmo probabilístico de primalidade. 
            Diferente da divisão por tentativas comum (que demora uma eternidade com números grandes), ele se baseia em propriedades estruturais de aritmética modular derivadas do **Pequeno Teorema de Fermat**.
            
            O algoritmo fatora $n-1$ como $2^r \\cdot d$. Em seguida, sorteia bases aleatórias $a$ e verifica se:
            - $a^d \\equiv 1 \\pmod n$ ou
            - $a^{2^s \\cdot d} \\equiv -1 \\pmod n$ para algum $0 \\le s < r$.
            
            Se o número falhar no teste para qualquer base, ele é **comprovadamente composto**. Se passar por várias rodadas, a chance de ele não ser primo é menor que $(1/4)^k$, sendo considerado um *primo provável*.
            """)

    with col2:
        st.subheader("2. Seleção de Chaves Combinadas")
        phi_atual = (st.session_state.P - 1) * (st.session_state.Q - 1)
        st.write(f"Módulo atual $N = {st.session_state.N}$ | Funçâo Totiente $\\phi(N) = {phi_atual}$")
        
        # Requisito 2: Calcula os pares na hora e exibe uma lista para o usuário selecionar
        chaves_disponiveis = get_valid_key_pairs(phi_atual)
        
        if chaves_disponiveis:
            st.write("Selecione um dos pares matematicamente compatíveis encontrados:")
            
            # Formata a exibição das opções para o usuário escolher
            opcoes_lista = [f"Pública (E): {c['Chave Pública (E)']} ➔ Privada (D): {c['Chave Privada (D)']}" for c in chaves_disponiveis]
            escolha = st.radio("Par de Chaves Ativo:", opcoes_lista)
            
            # Encontra o índice selecionado para aplicar no estado da sessão
            idx_selecionado = opcoes_lista.index(escolha)
            st.session_state.E = chaves_disponiveis[idx_selecionado]["Chave Pública (E)"]
            st.session_state.D = chaves_disponiveis[idx_selecionado]["Chave Privada (D)"]
            
            st.info(f"**Configuração ativa:** Chave Pública $E = {st.session_state.E}$ | Chave Privada $D = {st.session_state.D}$")
        else:
            st.error("Nenhum expoente padrão é coprimo com o seu φ(N). Tente mudar os primos.")

        with st.expander("📚 Como são geradas as Chaves E e D?"):
            st.write("""
            Para construir as chaves do RSA, seguimos as seguintes regras matemáticas:
            
            1. **Chave Pública (E):** Deve ser um número inteiro de modo que $1 < E < \\phi(N)$ e que seja **coprimo** com $\\phi(N)$, ou seja, $\\text{mdc}(E, \\phi(N)) = 1$.
            2. **Chave Privada (D):** É o **inverso multiplicativo modular** de $E \\pmod{\\phi(N)}$. Significa que precisamos resolver a equação:
            $$E \\cdot D \\equiv 1 \\pmod{\\phi(N)}$$
            
            Para encontrar $D$ de forma instantânea, o sistema utiliza o **Algoritmo Estendido de Euclides**, calculando os coeficientes da Identidade de Bézout que solucionam essa congruência linear.
            """)

    # Requisito 4: Cifragem da semente mantida intacta
    st.markdown("---")
    st.subheader("3. Cálculo Prático da Semente Híbrida")
    st.write("Abaixo está a demonstração real de como a semente atual seria enviada protegida pela matemática do RSA:")
    
    if st.session_state.original_seed is not None:
        semente_inteira = int(round(st.session_state.original_seed * 100000))
        
        st.write("**Processo de Cifragem da Semente (Lado do Emissor):**")
        st.write("A semente flutuante é convertida em um inteiro plano $M$ para a exponenciação modular:")
        st.latex(rf"C = M^E \pmod N")
        st.latex(rf"C = {semente_inteira}^{{{st.session_state.E}}} \pmod{{{st.session_state.N}}}")
        st.latex(rf"C = {st.session_state.encrypted_seed}")
        
        st.write("**Processo de Decifragem da Semente (Lado do Receptor):**")
        st.write("O receptor usa a sua chave privada $D$ selecionada na tabela para abrir o segredo:")
        st.latex(rf"M = C^D \pmod N")
        st.latex(rf"M = {st.session_state.encrypted_seed}^{{{st.session_state.D}}} \pmod{{{st.session_state.N}}}")
        st.latex(rf"M = {semente_inteira} \implies \div 100000 \implies {st.session_state.original_seed}")
    else:
        st.info("Insira uma semente caótica na barra lateral e clique em 'Cifrar Semente via RSA' para disparar os cálculos reais aqui.")