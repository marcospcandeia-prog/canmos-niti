'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { StatCard } from '@/components/StatCard';
import { Badge } from '@/components/Badge';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useToast } from '@/components/Toast';
import { useProfileStore } from '@/stores/profileStore';

function formatCPF(cpf: string): string {
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('pt-BR');
}

export default function ProfilePage() {
  const { toast } = useToast();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'info' | 'password' | 'privacy'>('info');
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({ nome: '', telefone: '', endereco: '', cidade: '', estado: '', cep: '', data_nascimento: '' });
  const [passwordData, setPasswordData] = useState({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);

  const {
    profile,
    stats,
    loading,
    saving,
    changingPassword,
    editError,
    editSuccess,
    passwordError,
    passwordSuccess,
    loadProfile,
    loadStats,
    updateProfile,
    changePassword,
    resetEditState,
    resetPasswordState,
  } = useProfileStore();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    await loadProfile();
    await loadStats();
    const p = useProfileStore.getState().profile;
    if (p) {
      setEditData({
        nome: p.nome || '',
        telefone: p.telefone || '',
        endereco: (p as any).endereco || '',
        cidade: (p as any).cidade || '',
        estado: (p as any).estado || '',
        cep: (p as any).cep || '',
        data_nascimento: p.data_nascimento || '',
      });
    }
  };

  const handleSaveProfile = async () => {
    resetEditState();
    const success = await updateProfile(editData);
    if (success) {
      setIsEditing(false);
      await loadData();
      setTimeout(() => resetEditState(), 3000);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    resetPasswordState();
    if (passwordData.nova_senha !== passwordData.confirmar_senha) {
      useProfileStore.setState({ passwordError: 'As senhas não coincidem' });
      return;
    }
    if (passwordData.nova_senha.length < 8) {
      useProfileStore.setState({ passwordError: 'A nova senha deve ter no mínimo 8 caracteres' });
      return;
    }
    const success = await changePassword(passwordData.senha_atual, passwordData.nova_senha);
    if (success) {
      setPasswordData({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
      setTimeout(() => resetPasswordState(), 3000);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) { toast('Digite sua senha para confirmar', 'warning'); return; }
    if (!confirm('TEM CERTEZA? Esta ação não pode ser desfeita. Todos os seus dados serão excluídos permanentemente após 30 dias.')) return;
    setDeleting(true);
    try {
      const { default: api } = await import('@/lib/api');
      await api.delete('/users/me', { data: { senha: deletePassword } });
      toast('Conta excluída.', 'success');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.push('/');
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao excluir conta', 'error');
      setDeleting(false);
    }
  };

  if (loading) return <LoadingSpinner message="Carregando perfil..." />;
  if (!profile) return null;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meu Perfil</h1>
          <p className="mt-1 text-sm text-gray-600">Gerencie suas informações pessoais</p>
        </div>
        <Badge label={profile.status === 'active' ? 'Ativa' : 'Inativa'} variant={profile.status === 'active' ? 'success' : 'default'} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatCard title="Documentos Enviados" value={stats?.total_documents || 0} color="blue" />
        <StatCard title="Declarações Criadas" value={stats?.declarations_count || 0} color="green" />
        <StatCard title="Membro Desde" value={formatDate(profile.created_at)} color="gray" />
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {(['info', 'password', 'privacy'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'info' ? 'Informações Pessoais' : tab === 'password' ? 'Segurança' : 'Privacidade & Dados'}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'info' && (
            <div>
              {editSuccess && <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg"><p className="text-sm text-green-800 font-medium">Perfil atualizado com sucesso!</p></div>}
              {editError && <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"><p className="text-sm text-red-800">{editError}</p></div>}

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <div className="px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-600">{profile.email}</div>
                    <p className="mt-1 text-xs text-gray-500">Email não pode ser alterado</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">CPF</label>
                    <div className="px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-600">{formatCPF(profile.cpf)}</div>
                    <p className="mt-1 text-xs text-gray-500">CPF não pode ser alterado</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InputField label="Nome Completo *" value={editData.nome} onChange={(v) => setEditData({...editData, nome: v})} disabled={!isEditing} />
                  <InputField label="Telefone" value={editData.telefone} onChange={(v) => setEditData({...editData, telefone: v})} disabled={!isEditing} placeholder="(00) 00000-0000" />
                </div>

                <InputField label="Endereço" value={editData.endereco} onChange={(v) => setEditData({...editData, endereco: v})} disabled={!isEditing} placeholder="Rua, número, complemento" />

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <InputField label="Cidade" value={editData.cidade} onChange={(v) => setEditData({...editData, cidade: v})} disabled={!isEditing} />
                  <InputField label="Estado" value={editData.estado} onChange={(v) => setEditData({...editData, estado: v})} disabled={!isEditing} placeholder="UF" maxLength={2} />
                  <InputField label="CEP" value={editData.cep} onChange={(v) => setEditData({...editData, cep: v})} disabled={!isEditing} placeholder="00000-000" />
                </div>

                <InputField label="Data de Nascimento" value={editData.data_nascimento} onChange={(v) => setEditData({...editData, data_nascimento: v})} disabled={!isEditing} type="date" />

                <div className="flex justify-end space-x-3 pt-4 border-t">
                  {!isEditing ? (
                    <button onClick={() => setIsEditing(true)} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium">
                      Editar Perfil
                    </button>
                  ) : (
                    <>
                      <button onClick={() => { setIsEditing(false); resetEditState(); loadData(); }} disabled={saving} className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
                        Cancelar
                      </button>
                      <button onClick={handleSaveProfile} disabled={saving} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400">
                        {saving ? 'Salvando...' : 'Salvar Alterações'}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'password' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Alterar Senha</h3>
              {passwordSuccess && <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg"><p className="text-sm text-green-800 font-medium">Senha alterada com sucesso!</p></div>}
              {passwordError && <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"><p className="text-sm text-red-800">{passwordError}</p></div>}
              <form onSubmit={handleChangePassword} className="space-y-6">
                <InputField label="Senha Atual *" value={passwordData.senha_atual} onChange={(v) => setPasswordData({...passwordData, senha_atual: v})} type="password" required />
                <InputField label="Nova Senha *" value={passwordData.nova_senha} onChange={(v) => setPasswordData({...passwordData, nova_senha: v})} type="password" required minLength={8} hint="Mínimo 8 caracteres" />
                <InputField label="Confirmar Nova Senha *" value={passwordData.confirmar_senha} onChange={(v) => setPasswordData({...passwordData, confirmar_senha: v})} type="password" required />
                <div className="flex justify-end pt-4 border-t">
                  <button type="submit" disabled={changingPassword} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400">
                    {changingPassword ? 'Alterando...' : 'Alterar Senha'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'privacy' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Seus Direitos (LGPD)</h3>
                <p className="text-sm text-gray-600 mb-4">De acordo com a Lei Geral de Proteção de Dados, você tem os seguintes direitos:</p>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start"><span className="text-green-600 mr-2">✓</span><span><strong>Acesso:</strong> Visualizar todos os dados que temos sobre você</span></li>
                  <li className="flex items-start"><span className="text-green-600 mr-2">✓</span><span><strong>Correção:</strong> Atualizar dados incorretos ou desatualizados</span></li>
                  <li className="flex items-start"><span className="text-green-600 mr-2">✓</span><span><strong>Portabilidade:</strong> Exportar seus dados em formato estruturado</span></li>
                  <li className="flex items-start"><span className="text-green-600 mr-2">✓</span><span><strong>Exclusão:</strong> Solicitar remoção permanente de seus dados</span></li>
                </ul>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={async () => {
                    try {
                      const token = localStorage.getItem('access_token');
                      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/me/export`, {
                        headers: { Authorization: `Bearer ${token}` },
                      });
                      if (!res.ok) throw new Error('Erro ao exportar');
                      const blob = await res.blob();
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `canmos_niti_dados_${profile.cpf}.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                      toast('Dados exportados com sucesso', 'success');
                    } catch {
                      toast('Erro ao exportar dados', 'error');
                    }
                  }}
                  className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition font-medium"
                >
                  Exportar Meus Dados
                </button>
                <Link href="/privacidade" className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium text-center">
                  Ver Política de Privacidade
                </Link>
              </div>

              <div className="pt-6 border-t">
                <h3 className="text-lg font-semibold text-red-600 mb-2">Zona de Perigo</h3>
                <p className="text-sm text-gray-600 mb-4">Esta ação é permanente e não pode ser desfeita.</p>
                {!showDeleteConfirm ? (
                  <button onClick={() => setShowDeleteConfirm(true)} className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium">
                    Excluir Minha Conta
                  </button>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-lg">
                    <h4 className="font-semibold text-red-900 mb-2">Confirmar Exclusão de Conta</h4>
                    <p className="text-sm text-red-700 mb-4">
                      Esta ação irá:<br />• Desativar sua conta imediatamente<br />• Excluir todos os seus dados após 30 dias<br />• Remover permanentemente documentos e declarações
                    </p>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-red-900 mb-2">Digite sua senha para confirmar:</label>
                      <input type="password" value={deletePassword} onChange={(e) => setDeletePassword(e.target.value)} className="w-full px-4 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500" placeholder="Senha" />
                    </div>
                    <div className="flex space-x-3">
                      <button onClick={() => { setShowDeleteConfirm(false); setDeletePassword(''); }} disabled={deleting} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
                        Cancelar
                      </button>
                      <button onClick={handleDeleteAccount} disabled={deleting || !deletePassword} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium disabled:bg-gray-400">
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
  );
}

function InputField({ label, value, onChange, disabled, type = 'text', placeholder, required, minLength, maxLength, hint }: {
  label: string; value: string; onChange: (v: string) => void; disabled?: boolean;
  type?: string; placeholder?: string; required?: boolean; minLength?: number; maxLength?: number; hint?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      {type === 'date' ? (
        <input type="date" value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            disabled ? 'border-gray-200 bg-gray-50 text-gray-600' : 'border-gray-300 bg-white'
          }`} />
      ) : (
        <input type={type} value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled}
          placeholder={placeholder} required={required} minLength={minLength} maxLength={maxLength}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
            disabled ? 'border-gray-200 bg-gray-50 text-gray-600' : 'border-gray-300 bg-white'
          }`} />
      )}
      {hint && <p className="mt-1 text-xs text-gray-500">{hint}</p>}
    </div>
  );
}
