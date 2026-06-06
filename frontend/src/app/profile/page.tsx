'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

interface UserProfile {
  id: string;
  email: string;
  cpf: string;
  nome: string;
  telefone: string | null;
  endereco: string | null;
  cidade: string | null;
  estado: string | null;
  cep: string | null;
  data_nascimento: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

interface UserStats {
  total_documents: number;
  documents_processed: number;
  total_tax_events: number;
  declarations_count: number;
  last_activity: string | null;
}

function formatCPF(cpf: string): string {
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'info' | 'password' | 'privacy'>('info');
  
  // Edit mode states
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    nome: '',
    telefone: '',
    endereco: '',
    cidade: '',
    estado: '',
    cep: '',
    data_nascimento: '',
  });
  const [saving, setSaving] = useState(false);
  const [editError, setEditError] = useState('');
  const [editSuccess, setEditSuccess] = useState(false);

  // Password change states
  const [passwordData, setPasswordData] = useState({
    senha_atual: '',
    nova_senha: '',
    confirmar_senha: '',
  });
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  // Delete account state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileRes, statsRes] = await Promise.all([
        api.get('/users/me'),
        api.get('/users/me/stats'),
      ]);

      setProfile(profileRes.data);
      setStats(statsRes.data);
      
      // Inicializa dados de edição
      setEditData({
        nome: profileRes.data.nome || '',
        telefone: profileRes.data.telefone || '',
        endereco: profileRes.data.endereco || '',
        cidade: profileRes.data.cidade || '',
        estado: profileRes.data.estado || '',
        cep: profileRes.data.cep || '',
        data_nascimento: profileRes.data.data_nascimento || '',
      });
    } catch (err: any) {
      console.error('Erro ao carregar dados:', err);
      if (err.response?.status === 401) {
        router.push('/auth/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setEditError('');
    setEditSuccess(false);
    setSaving(true);

    try {
      await api.put('/users/me', editData);
      setEditSuccess(true);
      setIsEditing(false);
      loadData();
      setTimeout(() => setEditSuccess(false), 3000);
    } catch (err: any) {
      setEditError(err.response?.data?.detail || 'Erro ao atualizar perfil');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess(false);

    if (passwordData.nova_senha !== passwordData.confirmar_senha) {
      setPasswordError('As senhas não coincidem');
      return;
    }

    if (passwordData.nova_senha.length < 8) {
      setPasswordError('A nova senha deve ter no mínimo 8 caracteres');
      return;
    }

    setChangingPassword(true);

    try {
      await api.post('/users/me/change-password', {
        senha_atual: passwordData.senha_atual,
        nova_senha: passwordData.nova_senha,
      });

      setPasswordSuccess(true);
      setPasswordData({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.response?.data?.detail || 'Erro ao alterar senha');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      alert('Digite sua senha para confirmar');
      return;
    }

    if (!confirm('TEM CERTEZA? Esta ação não pode ser desfeita. Todos os seus dados serão excluídos permanentemente após 30 dias.')) {
      return;
    }

    setDeleting(true);

    try {
      await api.delete('/users/me', {
        data: { senha: deletePassword }
      });

      alert('Conta excluída. Você será redirecionado para a página inicial.');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.push('/');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao excluir conta');
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando perfil...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
                ← Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Meu Perfil</h1>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              profile.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {profile.status === 'active' ? 'Ativa' : 'Inativa'}
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Documentos Enviados</p>
            <p className="mt-2 text-3xl font-bold text-blue-600">{stats?.total_documents || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Declarações Criadas</p>
            <p className="mt-2 text-3xl font-bold text-green-600">{stats?.declarations_count || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Membro Desde</p>
            <p className="mt-2 text-lg font-semibold text-gray-900">{formatDate(profile.created_at)}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('info')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                  activeTab === 'info'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Informações Pessoais
              </button>
              <button
                onClick={() => setActiveTab('password')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                  activeTab === 'password'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Segurança
              </button>
              <button
                onClick={() => setActiveTab('privacy')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                  activeTab === 'privacy'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Privacidade & Dados
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* Tab: Informações Pessoais */}
            {activeTab === 'info' && (
              <div>
                {editSuccess && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800 font-medium">Perfil atualizado com sucesso!</p>
                  </div>
                )}

                {editError && (
                  <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">{editError}</p>
                  </div>
                )}

                <div className="space-y-6">
                  {/* Email e CPF (não editáveis) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                      </label>
                      <div className="px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-600">
                        {profile.email}
                      </div>
                      <p className="mt-1 text-xs text-gray-500">Email não pode ser alterado</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CPF
                      </label>
                      <div className="px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-600">
                        {formatCPF(profile.cpf)}
                      </div>
                      <p className="mt-1 text-xs text-gray-500">CPF não pode ser alterado</p>
                    </div>
                  </div>

                  {/* Dados editáveis */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nome Completo *
                      </label>
                      <input
                        type="text"
                        value={editData.nome}
                        onChange={(e) => setEditData({ ...editData, nome: e.target.value })}
                        disabled={!isEditing}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                          isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Telefone
                      </label>
                      <input
                        type="tel"
                        value={editData.telefone}
                        onChange={(e) => setEditData({ ...editData, telefone: e.target.value })}
                        disabled={!isEditing}
                        placeholder="(00) 00000-0000"
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                          isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                        }`}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Endereço
                    </label>
                    <input
                      type="text"
                      value={editData.endereco}
                      onChange={(e) => setEditData({ ...editData, endereco: e.target.value })}
                      disabled={!isEditing}
                      placeholder="Rua, número, complemento"
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                        isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                      }`}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cidade
                      </label>
                      <input
                        type="text"
                        value={editData.cidade}
                        onChange={(e) => setEditData({ ...editData, cidade: e.target.value })}
                        disabled={!isEditing}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                          isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Estado
                      </label>
                      <input
                        type="text"
                        value={editData.estado}
                        onChange={(e) => setEditData({ ...editData, estado: e.target.value })}
                        disabled={!isEditing}
                        placeholder="UF"
                        maxLength={2}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                          isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CEP
                      </label>
                      <input
                        type="text"
                        value={editData.cep}
                        onChange={(e) => setEditData({ ...editData, cep: e.target.value })}
                        disabled={!isEditing}
                        placeholder="00000-000"
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                          isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                        }`}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Data de Nascimento
                    </label>
                    <input
                      type="date"
                      value={editData.data_nascimento}
                      onChange={(e) => setEditData({ ...editData, data_nascimento: e.target.value })}
                      disabled={!isEditing}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                        isEditing ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-50 text-gray-600'
                      }`}
                    />
                  </div>

                  {/* Buttons */}
                  <div className="flex justify-end space-x-3 pt-4 border-t">
                    {!isEditing ? (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                      >
                        Editar Perfil
                      </button>
                    ) : (
                      <>
                        <button
                          onClick={() => {
                            setIsEditing(false);
                            setEditError('');
                            loadData();
                          }}
                          disabled={saving}
                          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={handleSaveProfile}
                          disabled={saving}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400"
                        >
                          {saving ? 'Salvando...' : 'Salvar Alterações'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Tab: Segurança */}
            {activeTab === 'password' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Alterar Senha</h3>

                {passwordSuccess && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800 font-medium">Senha alterada com sucesso!</p>
                  </div>
                )}

                {passwordError && (
                  <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">{passwordError}</p>
                  </div>
                )}

                <form onSubmit={handleChangePassword} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Senha Atual *
                    </label>
                    <input
                      type="password"
                      value={passwordData.senha_atual}
                      onChange={(e) => setPasswordData({ ...passwordData, senha_atual: e.target.value })}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nova Senha *
                    </label>
                    <input
                      type="password"
                      value={passwordData.nova_senha}
                      onChange={(e) => setPasswordData({ ...passwordData, nova_senha: e.target.value })}
                      required
                      minLength={8}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="mt-1 text-xs text-gray-500">Mínimo 8 caracteres</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirmar Nova Senha *
                    </label>
                    <input
                      type="password"
                      value={passwordData.confirmar_senha}
                      onChange={(e) => setPasswordData({ ...passwordData, confirmar_senha: e.target.value })}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex justify-end pt-4 border-t">
                    <button
                      type="submit"
                      disabled={changingPassword}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400"
                    >
                      {changingPassword ? 'Alterando...' : 'Alterar Senha'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Tab: Privacidade & Dados */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Seus Direitos (LGPD)</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    De acordo com a Lei Geral de Proteção de Dados, você tem os seguintes direitos:
                  </p>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Acesso:</strong> Visualizar todos os dados que temos sobre você</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Correção:</strong> Atualizar dados incorretos ou desatualizados</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Portabilidade:</strong> Exportar seus dados em formato estruturado</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Exclusão:</strong> Solicitar remoção permanente de seus dados</span>
                    </li>
                  </ul>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => alert('Download de dados em desenvolvimento')}
                    className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition font-medium"
                  >
                    Exportar Meus Dados
                  </button>
                  <Link
                    href="/privacidade"
                    className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium text-center"
                  >
                    Ver Política de Privacidade
                  </Link>
                </div>

                <div className="pt-6 border-t">
                  <h3 className="text-lg font-semibold text-red-600 mb-2">Zona de Perigo</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Esta ação é permanente e não pode ser desfeita.
                  </p>

                  {!showDeleteConfirm ? (
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                    >
                      Excluir Minha Conta
                    </button>
                  ) : (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h4 className="font-semibold text-red-900 mb-2">Confirmar Exclusão de Conta</h4>
                      <p className="text-sm text-red-700 mb-4">
                        Esta ação irá:
                        <br />• Desativar sua conta imediatamente
                        <br />• Excluir todos os seus dados após 30 dias
                        <br />• Remover permanentemente documentos e declarações
                      </p>
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-red-900 mb-2">
                          Digite sua senha para confirmar:
                        </label>
                        <input
                          type="password"
                          value={deletePassword}
                          onChange={(e) => setDeletePassword(e.target.value)}
                          className="w-full px-4 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500"
                          placeholder="Senha"
                        />
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => {
                            setShowDeleteConfirm(false);
                            setDeletePassword('');
                          }}
                          disabled={deleting}
                          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={handleDeleteAccount}
                          disabled={deleting || !deletePassword}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium disabled:bg-gray-400"
                        >
                          {deleting ? 'Excluindo...' : 'Confirmar Exclusão'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
