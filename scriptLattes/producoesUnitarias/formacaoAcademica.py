#!/usr/bin/python
# encoding: utf-8
# filename: formacaoAcademica.py
#
#  scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
#
#  Este programa é um software livre; você pode redistribui-lo e/ou 
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como 
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da 
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util, 
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#



class FormacaoAcademica:
	anoInicio = None
	anoConclusao = None
	tipo = ''
	nomeInstituicao = ''
	descricao = ''

	def __init__(self, partesDoItem):
		# partesDoItem[0]: Periodo da formacao Profissional
		# partesDoItem[1]: Descricao da formacao Profissional

		anos =  partesDoItem[0].partition(" - ")
		self.anoInicio = anos[0];
		self.anoConclusao = anos[2];

		detalhe = partesDoItem[1].partition(".")
		self.tipo = detalhe[0].strip()

		detalhe = detalhe[2].strip().partition(".")
		self.nomeInstituicao = detalhe[0].strip()
		self.descricao = detalhe[2].strip()


	# ------------------------------------------------------------------------ #
	def __str__(self):
		s  = "\n[FORMACAO ACADEMICA] \n"
		s += "+ANO INICIO  : " + self.anoInicio.encode('utf8','replace') + "\n"
		s += "+ANO CONCLUS.: " + self.anoConclusao.encode('utf8','replace') + "\n"
		s += "+TIPO        : " + self.tipo.encode('utf8','replace') + "\n"
		s += "+INSTITUICAO : " + self.nomeInstituicao.encode('utf8','replace') + "\n"
		s += "+DESCRICAO   : " + self.descricao.encode('utf8','replace') + "\n"
		return s
