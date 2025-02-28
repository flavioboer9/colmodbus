import streamlit as st
import time
from pymodbus.client import ModbusTcpClient
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para verificar se o servidor Modbus está rodando
def verificar_conexao_modbus():
    """
    Verifica se o servidor Modbus está rodando.
    
    Returns:
        bool: True se o servidor estiver rodando, False caso contrário
    """
    host = "127.0.0.1"
    port = 5020
    
    print(f"Verificando conexão Modbus em {host}:{port}")
    
    # Criar cliente
    client = ModbusTcpClient(host=host, port=port)
    
    # Conectar
    connected = client.connect()
    print(f"Conexão: {connected}")
    
    if connected:
        # Ler registros para confirmar
        try:
            response = client.read_holding_registers(address=0, count=1)
            success = response is not None and not response.isError()
            print(f"Leitura de teste: {success}")
        except Exception as e:
            print(f"Erro na leitura de teste: {e}")
            success = False
        
        # Fechar conexão
        client.close()
        print("Conexão fechada")
        return success
    else:
        print("Falha na conexão")
        return False

# Função para ler os valores dos registros Modbus
def ler_registros_modbus():
    """
    Lê os valores dos registros Modbus do servidor.
    
    Returns:
        dict: Dicionário com os valores dos registros ou None se ocorrer um erro
    """
    host = "127.0.0.1"
    port = 5020
    
    # Criar cliente
    client = ModbusTcpClient(host=host, port=port)
    
    # Conectar
    if client.connect():
        try:
            # Ler registros
            response = client.read_holding_registers(address=0, count=4)
            
            if response is None or response.isError():
                client.close()
                return None
            
            # Extrair valores
            ativar = bool(response.registers[0])
            entregar = bool(response.registers[1])
            gaveta = response.registers[2]
            posicao_gaveta = response.registers[3]
            
            # Fechar conexão
            client.close()
            
            # Retornar valores
            return {
                "ativar": ativar,
                "entregar": entregar,
                "gaveta": gaveta,
                "posicao_gaveta": posicao_gaveta
            }
        except Exception as e:
            print(f"Erro ao ler registros: {e}")
            client.close()
            return None
    else:
        return None

# Inicializar estado da sessão
if 'last_full_refresh' not in st.session_state:
    st.session_state.last_full_refresh = time.time()
    st.session_state.refresh_interval = 30  # segundos
    st.session_state.valores_registros = None
    st.session_state.servidor_conectado = verificar_conexao_modbus()
    if st.session_state.servidor_conectado:
        st.session_state.valores_registros = ler_registros_modbus()

# Adicionar título e botão de refresh na mesma linha
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title("Monitoramento Modbus")
with col2:
    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    refresh_button = st.button("↻", help="Atualizar agora", key="refresh_button")
    
    # Estilo para o botão
    st.markdown("""
    <style>
    [data-testid="stButton"] > button {
        background-color: #FFB74D;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Usar um container customizado para o conteúdo
custom_container = st.container()

# Dentro do container customizado, criar o HTML para o conteúdo
with custom_container:
    # Adicionar o status de conexão
    status_class = "connected" if st.session_state.servidor_conectado else "disconnected"
    status_text = "Servidor Modbus Conectado" if st.session_state.servidor_conectado else "Servidor Modbus Desconectado"
    
    # Exibir o status de conexão
    st.markdown(f'''
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <div class="connection-status {status_class}"></div>
        <span>{status_text}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Adicionar espaço após o status
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # Adicionar os valores dos registros se disponíveis
    if st.session_state.servidor_conectado and st.session_state.valores_registros:
        valores_registros = st.session_state.valores_registros
        
        # Primeira linha: Ativar e Entregar
        col1, col2 = st.columns(2)
        
        with col1:
            ativar_valor = "LIGADO (1)" if valores_registros["ativar"] else "DESLIGADO (0)"
            ativar_class = "modbus-true" if valores_registros["ativar"] else "modbus-false"
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Ativar:</div>
                <div class="modbus-value {ativar_class}">{ativar_valor}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            entregar_valor = "LIGADO (1)" if valores_registros["entregar"] else "DESLIGADO (0)"
            entregar_class = "modbus-true" if valores_registros["entregar"] else "modbus-false"
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Entregar:</div>
                <div class="modbus-value {entregar_class}">{entregar_valor}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Segunda linha: Gaveta e Posição Gaveta
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Gaveta:</div>
                <div class="modbus-value modbus-number">{valores_registros["gaveta"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Pos. Gaveta:</div>
                <div class="modbus-value modbus-number">{valores_registros["posicao_gaveta"]}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        # Exibir mensagem se o servidor estiver desconectado
        if not st.session_state.servidor_conectado:
            st.warning("Servidor Modbus desconectado. Verifique a conexão e reinicie a aplicação.")
    
    # Processar o clique no botão de atualização
    if refresh_button:
        st.session_state.servidor_conectado = verificar_conexao_modbus()
        if st.session_state.servidor_conectado:
            st.session_state.valores_registros = ler_registros_modbus()
        st.rerun()
    
    # Adicionar seção para enviar novos valores para o servidor
    if st.session_state.servidor_conectado:
        # Adicionar espaço entre os containers
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # Abrir container com borda para o formulário
        st.markdown('''
        <div class="border-container">
        ''', unsafe_allow_html=True)
        
        # Criar formulário para envio de novos valores
        with st.form(key="enviar_valores_form"):
            col1, col2 = st.columns(2)
            
            # Primeira linha: Ativar e Entregar (boolean)
            with col1:
                novo_ativar = st.selectbox(
                    "Novo valor para Ativar:",
                    options=["Selecione...", "LIGADO", "DESLIGADO"],
                    index=0
                )
            
            with col2:
                novo_entregar = st.selectbox(
                    "Novo valor para Entregar:",
                    options=["Selecione...", "LIGADO", "DESLIGADO"],
                    index=0
                )
            
            # Segunda linha: Gaveta e Posição Gaveta (numeric)
            with col1:
                novo_gaveta = st.number_input(
                    "Novo valor para Gaveta:",
                    min_value=0,
                    max_value=100,
                    value=0
                )
            
            with col2:
                novo_posicao_gaveta = st.number_input(
                    "Novo valor para Pos. Gaveta:",
                    min_value=0,
                    max_value=100,
                    value=0
                )
            
            # Botão para enviar os valores
            enviar_button = st.form_submit_button(
                label="Enviar valores para o servidor",
                type="primary"
            )
            
            # Processar o envio dos valores quando o botão for clicado
            if enviar_button:
                import subprocess
                import os
                
                # Preparar os argumentos para o comando
                cmd = ["python", os.path.join(os.getcwd(), "src/main.py")]
                
                # Adicionar argumentos apenas para os campos que foram preenchidos
                if novo_ativar != "Selecione...":
                    cmd.append("--new-ativar")
                    cmd.append("true" if novo_ativar == "LIGADO" else "false")
                
                if novo_entregar != "Selecione...":
                    cmd.append("--new-entregar")
                    cmd.append("true" if novo_entregar == "LIGADO" else "false")
                
                if novo_gaveta > 0:
                    cmd.append("--new-gaveta")
                    cmd.append(str(novo_gaveta))
                
                if novo_posicao_gaveta > 0:
                    cmd.append("--new-posicao-gaveta")
                    cmd.append(str(novo_posicao_gaveta))
                
                # Executar o comando apenas se algum valor foi selecionado
                if len(cmd) > 2:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success("Valores enviados com sucesso para o servidor!")
                            # Atualizar os valores exibidos
                            st.session_state.valores_registros = ler_registros_modbus()
                            st.rerun()
                        else:
                            st.error(f"Erro ao enviar valores: {result.stderr}")
                    except Exception as e:
                        st.error(f"Erro ao executar o comando: {str(e)}")
                else:
                    st.warning("Nenhum valor foi selecionado para enviar.")
        
        # Fechar o container com borda
        st.markdown('</div>', unsafe_allow_html=True)
    
# Aplicar CSS personalizado
st.markdown("""
<style>
.connection-status {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}
.connected {
    background-color: #4CAF50;
}
.disconnected {
    background-color: #F44336;
}
.modbus-row {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
.modbus-label {
    font-weight: bold;
    width: 120px;
    margin-right: 10px;
}
.modbus-value {
    padding: 10px 15px;
    border-radius: 4px;
    font-weight: bold;
    min-width: 100px;
    text-align: center;
}
.modbus-true {
    background-color: #e8f5e9;
    color: #2e7d32;
}
.modbus-false {
    background-color: #ffebee;
    color: #c62828;
}
.modbus-number {
    background-color: #e8f0fe;
    color: #1a73e8;
}
.refresh-button {
    background: none;
    border: none;
    color: #1a73e8;
    cursor: pointer;
    font-size: 20px;
    margin-left: 10px;
    padding: 0;
    vertical-align: middle;
}
.refresh-button:hover {
    color: #174ea6;
}
.status-container {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
button[kind="secondary"] {
    background-color: #FFB74D !important;
    color: white !important;
    border: none !important;
}
.border-container {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
}
.container-title {
    position: absolute;
    top: -12px;
    left: 20px;
    background-color: white;
    padding: 0 10px;
    font-weight: 500;
    color: #555;
}
</style>
""", unsafe_allow_html=True)
