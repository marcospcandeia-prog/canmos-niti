'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

// Validador de CPF
function validarCPF(cpf: string): boolean {
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(cpf)) return false;
  
  let soma = 0;
  let resto;
  
  for (let i = 1; i <= 9; i++) {
    soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
  }
  
  resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpf.substring(9, 10))) return false;
  
  soma = 0;
  for (let i = 1; i <= 10; i++) {
    soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
  }
  
  resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpf.substring(10, 11))) return false;
  
  return true;
}

// Formatador de CPF
function formatarCPF(cpf: string): string {
  cpf = cpf.replace(/[^\d]/g, '');
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    nome_completo: '',
    email: '',
    cpf: '',
    senha: '',
    confirmarSenha: '',
    aceitouTermos: false,
  });

  const [errors, setErrors] = useState({
    nome_completo: '',
    email: '',
    cpf: '',
    senha: '',
    confirmarSenha: '',
    aceitouTermos: '',
  });

  const handleCPFChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const cpf = e.target.value.replace(/[^\d]/g, '');
    if (cpf.length <= 11) {
      setFormData({ ...formData, cpf });
      setErrors({ ...errors, cpf: '' });
    }
  };

  const validateForm = (): boolean => {
    const newErrors = {
      nome_completo: '',
      email: '',
      cpf: '',
      senha: '',
      confirmarSenha: '',
      aceitouTermos: '',
    };

    let isValid = true;

    // Nome completo
    if (!formData.nome_completo.trim()) {
      newErrors.nome_completo = 'Nome completo é obrigatório';
      isValid = false;
    } else if (formData.nome_completo.trim().split(' ').length < 2) {
      newErrors.nome_completo = 'Digite seu nome completo';
      isValid = false;
    }

    // Email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = 'Email é obrigatório';
      isValid = false;
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Email inválido';
      isValid = false;
    }

    // CPF
    if (!formData.cpf) {
      newErrors.cpf = 'CPF é obrigatório';
      isValid = false;
    } else if (!validarCPF(formData.cpf)) {
      newErrors.cpf = 'CPF inválido';
      isValid = false;
    }

    // Senha
    if (!formData.senha) {
      newErrors.senha = 'Senha é obrigatória';
      isValid = false;
    } else if (formData.senha.length < 8) {
      newErrors.senha = 'Senha deve ter no mínimo 8 caracteres';
      isValid = false;
    }

    // Confirmar senha
    if (!formData.confirmarSenha) {
      newErrors.confirmarSenha = 'Confirmação de senha é obrigatória';
      isValid = false;
    } else if (formData.senha !== formData.confirmarSenha) {
      newErrors.confirmarSenha = 'As senhas não coincidem';
      isValid = false;
    }

    // Termos
    if (!formData.aceitouTermos) {
      newErrors.aceitouTermos = 'Você deve aceitar os termos para continuar';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await api.post('/auth/register', {
        nome: formData.nome_completo,
        email: formData.email,
        cpf: formData.cpf,
        senha: formData.senha,
        lgpd_consent: true,
      });

      setSuccess(true);
      
      // Redirecionar para login após 2 segundos
      setTimeout(() => {
        router.push('/auth/login?registered=true');
      }, 2000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Erro ao criar conta. Verifique os dados e tente novamente.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Criar Conta
            </h1>
            <p className="text-gray-600">
              Gerencie suas declarações de forma inteligente
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm font-medium">
                Conta criada com sucesso! Redirecionando para login...
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Nome Completo */}
            <div>
              <label htmlFor="nome_completo" className="block text-sm font-medium text-gray-700 mb-1">
                Nome Completo *
              </label>
              <input
                id="nome_completo"
                type="text"
                placeholder="João da Silva"
                value={formData.nome_completo}
                onChange={(e) => {
                  setFormData({ ...formData, nome_completo: e.target.value });
                  setErrors({ ...errors, nome_completo: '' });
                }}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  errors.nome_completo ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading || success}
              />
              {errors.nome_completo && (
                <p className="mt-1 text-sm text-red-600">{errors.nome_completo}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={formData.email}
                onChange={(e) => {
                  setFormData({ ...formData, email: e.target.value });
                  setErrors({ ...errors, email: '' });
                }}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading || success}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* CPF */}
            <div>
              <label htmlFor="cpf" className="block text-sm font-medium text-gray-700 mb-1">
                CPF *
              </label>
              <input
                id="cpf"
                type="text"
                placeholder="000.000.000-00"
                value={formatarCPF(formData.cpf)}
                onChange={handleCPFChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  errors.cpf ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading || success}
              />
              {errors.cpf && (
                <p className="mt-1 text-sm text-red-600">{errors.cpf}</p>
              )}
            </div>

            {/* Senha */}
            <div>
              <label htmlFor="senha" className="block text-sm font-medium text-gray-700 mb-1">
                Senha *
              </label>
              <input
                id="senha"
                type="password"
                placeholder="Mínimo 8 caracteres"
                value={formData.senha}
                onChange={(e) => {
                  setFormData({ ...formData, senha: e.target.value });
                  setErrors({ ...errors, senha: '' });
                }}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  errors.senha ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading || success}
              />
              {errors.senha && (
                <p className="mt-1 text-sm text-red-600">{errors.senha}</p>
              )}
            </div>

            {/* Confirmar Senha */}
            <div>
              <label htmlFor="confirmarSenha" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Senha *
              </label>
              <input
                id="confirmarSenha"
                type="password"
                placeholder="Digite a senha novamente"
                value={formData.confirmarSenha}
                onChange={(e) => {
                  setFormData({ ...formData, confirmarSenha: e.target.value });
                  setErrors({ ...errors, confirmarSenha: '' });
                }}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition ${
                  errors.confirmarSenha ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading || success}
              />
              {errors.confirmarSenha && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmarSenha}</p>
              )}
            </div>

            {/* Termos LGPD */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-start">
                <input
                  id="termos"
                  type="checkbox"
                  checked={formData.aceitouTermos}
                  onChange={(e) => {
                    setFormData({ ...formData, aceitouTermos: e.target.checked });
                    setErrors({ ...errors, aceitouTermos: '' });
                  }}
                  className={`mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                    errors.aceitouTermos ? 'border-red-500' : ''
                  }`}
                  disabled={loading || success}
                />
                <label htmlFor="termos" className="ml-3 text-sm text-gray-700">
                  Aceito os{' '}
                  <Link href="/termos" className="text-blue-600 hover:underline">
                    Termos de Uso
                  </Link>{' '}
                  e a{' '}
                  <Link href="/privacidade" className="text-blue-600 hover:underline">
                    Política de Privacidade (LGPD)
                  </Link>
                  . Concordo com o tratamento dos meus dados pessoais conforme descrito.
                </label>
              </div>
              {errors.aceitouTermos && (
                <p className="mt-2 text-sm text-red-600">{errors.aceitouTermos}</p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || success}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Criando conta...' : success ? 'Conta criada!' : 'Criar Conta'}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Já tem uma conta?{' '}
              <Link href="/auth/login" className="text-blue-600 hover:underline font-medium">
                Fazer login
              </Link>
            </p>
          </div>
        </div>

        {/* Info LGPD */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-600">
            Seus dados são protegidos de acordo com a LGPD (Lei 13.709/2018).
            <br />
            Você pode solicitar acesso, correção ou exclusão a qualquer momento.
          </p>
        </div>
      </div>
    </div>
  );
}
