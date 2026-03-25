"""
Testes automatizados para o sistema de permissões baseado em grupos.

Este módulo testa os 12 cenários descritos no TESTING_GUIDE.md:
1. Vendedor cria cliente (auto-atribuído)
2. Admin cria cliente e atribui a vendedor
3. Vendedor lista clientes (só seus)
4. Admin lista clientes (todos)
5. Vendedor tenta acessar cliente de outro vendedor (404)
6. Vendedor cria telefone para seu cliente
7. Vendedor tenta criar telefone para cliente de outro (400)
8. Vendedor lista telefones (filtrado)
9. Admin altera responsável de cliente
10. Vendedor tenta alterar responsável (ignorado)
11. Buscar clientes por responsável
12. Buscar telefones por responsável do cliente
"""

from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Clients, Notas, Phone


class BaseTestCase(APITestCase):
    """Classe base com fixtures compartilhadas."""
    
    @classmethod
    def setUpTestData(cls):
        """Cria grupos, usuários e dados de teste."""
        # Criar grupos
        cls.grupo_vendedor = Group.objects.create(name='Vendedor')
        cls.grupo_admin = Group.objects.create(name='Administrador')
        
        # Criar usuários vendedores
        cls.joao = User.objects.create_user(
            username='joao',
            password='senha123',
            first_name='João',
            last_name='Silva',
            is_staff=True
        )
        cls.joao.groups.add(cls.grupo_vendedor)
        
        cls.maria = User.objects.create_user(
            username='maria',
            password='senha123',
            first_name='Maria',
            last_name='Santos',
            is_staff=True
        )
        cls.maria.groups.add(cls.grupo_vendedor)
        
        cls.pedro = User.objects.create_user(
            username='pedro',
            password='senha123',
            first_name='Pedro',
            last_name='Costa',
            is_staff=True
        )
        cls.pedro.groups.add(cls.grupo_vendedor)
        
        # Criar usuários administradores
        cls.marcela = User.objects.create_user(
            username='marcela',
            password='admin123',
            first_name='Marcela',
            last_name='Admin',
            is_staff=True
        )
        cls.marcela.groups.add(cls.grupo_admin)
        
        cls.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            first_name='Admin',
            last_name='System',
            is_staff=True,
            is_superuser=True
        )
        cls.admin.groups.add(cls.grupo_admin)
        
        # Criar alguns clientes iniciais
        cls.cliente_joao = Clients.objects.create(
            name='Cliente do João',
            email='cliente.joao@email.com',
            responsavel=cls.joao
        )
        
        cls.cliente_maria = Clients.objects.create(
            name='Cliente da Maria',
            email='cliente.maria@email.com',
            responsavel=cls.maria
        )
        
        # Criar alguns telefones
        cls.telefone_joao = Phone.objects.create(
            number='5561999888777',
            tipo='CEL',
            client=cls.cliente_joao
        )
        
        cls.telefone_maria = Phone.objects.create(
            number='5561988887777',
            tipo='WHATS',
            client=cls.cliente_maria
        )
        
        # Criar algumas notas
        cls.nota_joao = Notas.objects.create(
            texto='Nota do cliente do João',
            client=cls.cliente_joao
        )


class Teste01VendedorCriaClienteAutoAtribuido(BaseTestCase):
    """Teste 1: Vendedor cria cliente e é auto-atribuído como responsável."""
    
    def test_vendedor_cria_cliente_auto_atribuido(self):
        """Vendedor cria cliente e o sistema atribui automaticamente como responsável."""
        self.client.force_authenticate(user=self.joao)
        
        data = {
            'name': 'Novo Cliente do João',
            'email': 'novo.cliente.joao@email.com'
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Novo Cliente do João')
        self.assertEqual(response.data['email'], 'novo.cliente.joao@email.com')
        
        # Verificar que o responsável é o João
        self.assertEqual(response.data['responsavel']['username'], 'joao')
        self.assertEqual(response.data['responsavel']['id'], self.joao.id)
        
        # Verificar que o campo responsavel_id não aparece (vendedor não pode escolher)
        self.assertNotIn('responsavel_id', response.data)
        
        # Verificar no banco de dados
        cliente_criado = Clients.objects.get(email='novo.cliente.joao@email.com')
        self.assertEqual(cliente_criado.responsavel, self.joao)


class Teste02AdminCriaClienteEAtribuiAVendedor(BaseTestCase):
    """Teste 2: Admin cria cliente e atribui a um vendedor específico."""
    
    def test_admin_cria_cliente_e_atribui_a_vendedor(self):
        """Admin cria cliente e escolhe o responsável."""
        self.client.force_authenticate(user=self.marcela)
        
        data = {
            'name': 'Cliente Atribuído a Pedro',
            'email': 'cliente.pedro@email.com',
            'responsavel_id': self.pedro.id
        }
        
        response = self.client.post('/api/v1/clientes', data, format='json')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Cliente Atribuído a Pedro')
        
        # Verificar que o responsável é Pedro (não Marcela!)
        self.assertEqual(response.data['responsavel']['username'], 'pedro')
        self.assertEqual(response.data['responsavel']['id'], self.pedro.id)
        
        # Verificar no banco de dados
        cliente_criado = Clients.objects.get(email='cliente.pedro@email.com')
        self.assertEqual(cliente_criado.responsavel, self.pedro)


class Teste03VendedorListaClientesSoSeus(BaseTestCase):
    """Teste 3: Vendedor lista clientes e vê apenas os seus."""
    
    def test_vendedor_lista_apenas_seus_clientes(self):
        """Vendedor lista clientes e vê apenas os que ele é responsável."""
        self.client.force_authenticate(user=self.joao)
        
        response = self.client.get('/api/v1/clientes')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # João deve ver apenas seus clientes
        clientes_ids = [c['id'] for c in response.data]
        self.assertIn(self.cliente_joao.id, clientes_ids)
        self.assertNotIn(self.cliente_maria.id, clientes_ids)
        
        # Verificar que todos os clientes retornados pertencem ao João
        for cliente in response.data:
            self.assertEqual(cliente['responsavel']['username'], 'joao')


class Teste04AdminListaClientesTodos(BaseTestCase):
    """Teste 4: Admin lista clientes e vê todos."""
    
    def test_admin_lista_todos_os_clientes(self):
        """Admin lista clientes e vê todos, independente do responsável."""
        self.client.force_authenticate(user=self.marcela)
        
        response = self.client.get('/api/v1/clientes')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin deve ver todos os clientes
        clientes_ids = [c['id'] for c in response.data]
        self.assertIn(self.cliente_joao.id, clientes_ids)
        self.assertIn(self.cliente_maria.id, clientes_ids)
        
        # Deve ter pelo menos 2 clientes de responsáveis diferentes
        responsaveis = set(c['responsavel']['username'] for c in response.data)
        self.assertGreaterEqual(len(responsaveis), 2)


class Teste05VendedorTentaAcessarClienteDeOutro(BaseTestCase):
    """Teste 5: Vendedor tenta acessar cliente de outro vendedor (404)."""
    
    def test_vendedor_nao_pode_acessar_cliente_de_outro(self):
        """Vendedor tentando acessar cliente de outro vendedor recebe 404."""
        self.client.force_authenticate(user=self.joao)
        
        # João tenta acessar cliente da Maria (ID do cliente_maria)
        response = self.client.get(f'/api/v1/clientes/{self.cliente_maria.id}')
        
        # Deve retornar 404 (não 403, por segurança)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Qualquer mensagem de 404 é válida
        self.assertIn('detail', response.data)


class Teste06VendedorCriaTelefoneParaSeuCliente(BaseTestCase):
    """Teste 6: Vendedor cria telefone para seu próprio cliente."""
    
    def test_vendedor_cria_telefone_para_seu_cliente(self):
        """Vendedor cria telefone para cliente que ele é responsável."""
        self.client.force_authenticate(user=self.joao)
        
        data = {
            'number': '5561987654321',
            'tipo': 'WHATS',
            'client_id': self.cliente_joao.id
        }
        
        response = self.client.post('/api/v1/telefones', data, format='json')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['number'], '5561987654321')
        self.assertEqual(response.data['tipo'], 'WHATS')
        self.assertEqual(response.data['client_name'], 'Cliente do João')
        
        # Verificar no banco de dados
        telefone_criado = Phone.objects.get(number='5561987654321')
        self.assertEqual(telefone_criado.client, self.cliente_joao)


class Teste07VendedorTentaCriarTelefoneParaClienteDeOutro(BaseTestCase):
    """Teste 7: Vendedor tenta criar telefone para cliente de outro vendedor (400)."""
    
    def test_vendedor_nao_pode_criar_telefone_para_cliente_de_outro(self):
        """Vendedor tentando criar telefone para cliente de outro recebe erro de validação."""
        self.client.force_authenticate(user=self.joao)
        
        data = {
            'number': '5561911112222',
            'tipo': 'CEL',
            'client_id': self.cliente_maria.id  # Cliente da Maria
        }
        
        response = self.client.post('/api/v1/telefones', data, format='json')
        
        # Deve retornar 400 com erro de validação
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client_id', response.data)
        # Mensagem pode estar em inglês ou português
        error_msg = str(response.data['client_id']).lower()
        self.assertTrue('invalid' in error_msg or 'inválido' in error_msg)


class Teste08VendedorListaTelefonesFiltrado(BaseTestCase):
    """Teste 8: Vendedor lista telefones e vê apenas dos seus clientes."""
    
    def test_vendedor_lista_apenas_telefones_de_seus_clientes(self):
        """Vendedor lista telefones e vê apenas os de clientes que ele é responsável."""
        self.client.force_authenticate(user=self.joao)
        
        response = self.client.get('/api/v1/telefones')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # João deve ver apenas telefones de seus clientes
        telefones_ids = [t['id'] for t in response.data]
        self.assertIn(self.telefone_joao.id, telefones_ids)
        self.assertNotIn(self.telefone_maria.id, telefones_ids)
        
        # Verificar que todos os telefones pertencem a clientes do João
        for telefone in response.data:
            self.assertIn('João', telefone['client_name'])


class Teste09AdminAlteraResponsavelDeCliente(BaseTestCase):
    """Teste 9: Admin altera o responsável de um cliente."""
    
    def test_admin_altera_responsavel_de_cliente(self):
        """Admin pode mudar o responsável de um cliente."""
        self.client.force_authenticate(user=self.marcela)
        
        # Alterar cliente do João para ser da Maria
        data = {
            'responsavel_id': self.maria.id
        }
        
        response = self.client.patch(
            f'/api/v1/clientes/{self.cliente_joao.id}',
            data,
            format='json'
        )
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responsavel']['username'], 'maria')
        self.assertEqual(response.data['responsavel']['id'], self.maria.id)
        
        # Verificar no banco de dados
        self.cliente_joao.refresh_from_db()
        self.assertEqual(self.cliente_joao.responsavel, self.maria)


class Teste10VendedorTentaAlterarResponsavel(BaseTestCase):
    """Teste 10: Vendedor tenta alterar responsável mas é ignorado."""
    
    def test_vendedor_nao_pode_alterar_responsavel(self):
        """Vendedor tenta mudar o responsável mas o campo é ignorado."""
        self.client.force_authenticate(user=self.joao)
        
        # João tenta mudar o responsável do seu cliente
        data = {
            'name': 'Nome Atualizado',
            'responsavel_id': self.pedro.id  # Tentando mudar para Pedro
        }
        
        response = self.client.patch(
            f'/api/v1/clientes/{self.cliente_joao.id}',
            data,
            format='json'
        )
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Nome foi atualizado
        self.assertEqual(response.data['name'], 'Nome Atualizado')
        
        # Responsável NÃO foi alterado (continua João)
        self.assertEqual(response.data['responsavel']['username'], 'joao')
        self.assertEqual(response.data['responsavel']['id'], self.joao.id)
        
        # Verificar no banco de dados
        self.cliente_joao.refresh_from_db()
        self.assertEqual(self.cliente_joao.responsavel, self.joao)


class Teste11BuscarClientesPorResponsavel(BaseTestCase):
    """Teste 11: Buscar clientes filtrando por responsável."""
    
    def test_admin_busca_clientes_por_responsavel(self):
        """Admin pode filtrar clientes por responsável específico."""
        self.client.force_authenticate(user=self.marcela)
        
        # Buscar clientes do João
        response = self.client.get(f'/api/v1/clientes?responsavel={self.joao.id}')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas clientes do João
        for cliente in response.data:
            self.assertEqual(cliente['responsavel']['id'], self.joao.id)
        
        # Buscar clientes da Maria
        response = self.client.get(f'/api/v1/clientes?responsavel={self.maria.id}')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas clientes da Maria
        for cliente in response.data:
            self.assertEqual(cliente['responsavel']['id'], self.maria.id)


class Teste12BuscarTelefonesPorResponsavelDoCliente(BaseTestCase):
    """Teste 12: Buscar telefones filtrando por responsável do cliente."""
    
    def test_admin_busca_telefones_por_responsavel_do_cliente(self):
        """Admin pode filtrar telefones pelo responsável do cliente."""
        self.client.force_authenticate(user=self.marcela)
        
        # Buscar telefones de clientes do João
        response = self.client.get(f'/api/v1/telefones?client__responsavel={self.joao.id}')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas telefones de clientes do João
        telefones_ids = [t['id'] for t in response.data]
        self.assertIn(self.telefone_joao.id, telefones_ids)
        self.assertNotIn(self.telefone_maria.id, telefones_ids)
        
        # Buscar telefones de clientes da Maria
        response = self.client.get(f'/api/v1/telefones?client__responsavel={self.maria.id}')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas telefones de clientes da Maria
        telefones_ids = [t['id'] for t in response.data]
        self.assertIn(self.telefone_maria.id, telefones_ids)
        self.assertNotIn(self.telefone_joao.id, telefones_ids)


class TestePermissoesNotas(BaseTestCase):
    """Testes adicionais para validar permissões em notas."""
    
    def test_vendedor_lista_apenas_notas_de_seus_clientes(self):
        """Vendedor vê apenas notas de clientes que ele é responsável."""
        self.client.force_authenticate(user=self.joao)
        
        response = self.client.get('/api/v1/notas')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # João deve ver apenas notas de seus clientes
        for nota in response.data:
            self.assertIn('João', nota['client_name'])
    
    def test_admin_lista_todas_as_notas(self):
        """Admin vê todas as notas de todos os clientes."""
        self.client.force_authenticate(user=self.marcela)
        
        response = self.client.get('/api/v1/notas')
        
        # Validações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin deve ver notas de diferentes responsáveis
        self.assertGreaterEqual(len(response.data), 1)


class TesteIntegracaoCompleta(BaseTestCase):
    """Teste de integração: fluxo completo vendedor -> admin."""
    
    def test_fluxo_completo_vendedor_cria_admin_transfere(self):
        """
        Cenário completo:
        1. Vendedor (João) cria cliente
        2. Vendedor cria telefone e nota para o cliente
        3. Admin (Marcela) transfere cliente para outro vendedor (Maria)
        4. João não vê mais o cliente
        5. Maria agora vê o cliente
        """
        # 1. João cria cliente
        self.client.force_authenticate(user=self.joao)
        
        cliente_data = {
            'name': 'Cliente Teste Integração',
            'email': 'integracao@email.com'
        }
        response = self.client.post('/api/v1/clientes', cliente_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cliente_id = response.data['id']
        
        # 2. João cria telefone e nota
        telefone_data = {
            'number': '5561999999999',
            'tipo': 'CEL',
            'client_id': cliente_id
        }
        response = self.client.post('/api/v1/telefones', telefone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        telefone_id = response.data['id']
        
        nota_data = {
            'texto': 'Nota de teste',
            'client_id': cliente_id
        }
        response = self.client.post('/api/v1/notas', nota_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        nota_id = response.data['id']
        
        # 3. Admin transfere cliente para Maria
        self.client.force_authenticate(user=self.marcela)
        
        transfer_data = {'responsavel_id': self.maria.id}
        response = self.client.patch(
            f'/api/v1/clientes/{cliente_id}',
            transfer_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responsavel']['username'], 'maria')
        
        # 4. João não vê mais o cliente
        self.client.force_authenticate(user=self.joao)
        
        response = self.client.get(f'/api/v1/clientes/{cliente_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.get(f'/api/v1/telefones/{telefone_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.get(f'/api/v1/notas/{nota_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 5. Maria agora vê o cliente, telefone e nota
        self.client.force_authenticate(user=self.maria)
        
        response = self.client.get(f'/api/v1/clientes/{cliente_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responsavel']['username'], 'maria')
        
        response = self.client.get(f'/api/v1/telefones/{telefone_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(f'/api/v1/notas/{nota_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
