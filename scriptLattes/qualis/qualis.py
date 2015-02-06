#!/usr/bin/python
# encoding: utf-8
# filename: qualis.py
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
# http://scriptlattes.sourceforge.net/
# Pacote desenvolvido por Helena Caseli
#
# Este programa é um software livre; você pode redistribui-lo e/ou
# modifica-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util,
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import re
import sys
import fileinput

from scriptLattes.util import compararCadeias, buscarArquivo
from qualis_extractor import *


def inicializa_lista_qualis(lista):
    lista['A1'] = 0
    lista['A2'] = 0
    lista['B1'] = 0
    lista['B2'] = 0
    lista['B3'] = 0
    lista['B4'] = 0
    lista['B5'] = 0
    lista['C'] = 0
    lista['Qualis nao identificado'] = 0


def parar():
    sys.stdin.read(1)


def padronizarNome(nome):
    nome = nome.replace(u"\u00A0", " ")
    nome = nome.replace(u"\u2010", " ")
    nome = nome.replace(u"-", " ")

    # nome = re.sub(r"\(.*\)", " ", nome)
    # nome = re.sub(r"\(", " ", nome)
    # nome = re.sub(r"\)", " ", nome)
    nome = re.sub("\s+", ' ', nome)
    nome = nome.strip()
    return nome


def inicializaTabelaDosTipos(tabela_tipos):
    inicializa_lista_qualis(tabela_tipos)


def calcularTotaisDosQualisPorTipo(qtd, lista_completa):
    inicializa_lista_qualis(qtd)
    keys = lista_completa.keys()
    if len(keys) > 0:
        for ano in keys:
            elementos = lista_completa[ano]
            for index in range(0, len(elementos)):
                pub = elementos[index]
                qtd[pub.qualis] += 1
    return qtd


def carregarQualis(arquivo):
    lista = {}
    if not arquivo == '':
        arquivo = buscarArquivo(arquivo)

        for linha in fileinput.input(arquivo):
            linha = linha.replace("\r", "")
            linha = linha.replace("\n", "")

            campos = linha.split('\t')
            sigla = campos[0].rstrip().decode("utf8")  # ISSN de periodicos ou SIGLA de congressos
            nome = campos[1].rstrip().decode("utf8")  # Nome do periodico ou evento
            qualis = campos[2].rstrip()  # Estrato Qualis

            nome = padronizarNome(nome)
            sigla = padronizarNome(sigla)

            lista[nome] = qualis
            lista[sigla] = qualis  # Armazena a sigla/issn do evento/periodico

        print "[QUALIS]: " + str(len(lista)) + " itens adicionados de " + arquivo
    return lista


class Qualis:
    periodicos = {}
    congressos = {}
    qtdPB0 = {}  # Total de artigos em periodicos por Qualis
    qtdPB4 = {}  # Total de trabalhos completos em congressos por Qualis
    qtdPB5 = {}  # Total de resumos expandidos em congressos por Qualis
    anoInicio = 0
    anoFim = 0

    def __init__(self, grupo):

        self.anoInicio = int(grupo.obterParametro('global-itens_desde_o_ano'))
        self.anoFim = int(grupo.obterParametro('global-itens_ate_o_ano'))

        if grupo.obterParametro('global-identificar_publicacoes_com_qualis'):
            # self.periodicos = self.carregarQualis(grupo.obterParametro('global-arquivo_qualis_de_periodicos'))
            # qualis extractor -> extrai qualis diretamente da busca online do qualis
            self.extrair_qualis_online = grupo.obterParametro('global-extrair_qualis_online')
            # self.extrair_qualis_online = grupo.diretorioCache is not ''
            self.qextractor = qualis_extractor(self.extrair_qualis_online)

            arqareas = grupo.obterParametro('global-arquivo_areas_qualis')
            self.qextractor.parse_areas_file(arqareas)

            filename = 'qualis.dump'
            if grupo.diretorioCache:
                filename = grupo.diretorioCache + '/' + filename

            if not self.extrair_qualis_online:
                print "\n**************************************************\n"
                self.qextractor.load_data(filename)
                # self.qextractor.extract_qualis()
                self.periodicos = self.qextractor.publicacao

                self.qextractor.save_data(filename)

            self.congressos = carregarQualis(grupo.obterParametro('global-arquivo_qualis_de_congressos'))

    def qualisPorAno(self, membro):

        tabelaDosAnos = [{}]
        tabelaDosTipos = {}

        self.inicializaTabelaDosAnos(tabelaDosAnos)
        inicializaTabelaDosTipos(tabelaDosTipos)

        if membro.listaArtigoEmPeriodico > 0:
            for publicacao in membro.listaArtigoEmPeriodico:
                if publicacao.qualis:
                    for tipo in publicacao.qualis.values():
                        valorAtual = self.getTiposPeloAno(publicacao.ano, tabelaDosAnos)[tipo]
                        self.setValorPeloAnoTipo(publicacao.ano, tipo, valorAtual + 1, tabelaDosAnos)
                        tabelaDosTipos[tipo] += 1

        membro.tabelaQualisDosAnos = tabelaDosAnos
        membro.tabelaQualisDosTipos = tabelaDosTipos

        return [tabelaDosAnos, tabelaDosTipos]

    def inicializaTabelaDosAnos(self, tabelaDosAnos):
        fim = self.anoFim - self.anoInicio
        for i in range(fim + 1):
            tabelaDosAnos.append({})
            inicializa_lista_qualis(tabelaDosAnos[i])

    def getTiposPeloAno(self, ano, tabelaDosAnos):
        if self.anoInicio <= ano <= self.anoFim:
            return tabelaDosAnos[ano - self.anoInicio]
        else:
            raise Exception(
                "Ano fora do limite" "O ano " + str(ano) + " nao esta no limite determinado nas configuracoes")

    def setValorPeloAnoTipo(self, ano, tipo, valor, tabelaDosAnos):
        if self.anoInicio <= ano <= self.anoFim:
            tabelaDosAnos[ano - self.anoInicio][tipo] = valor
        else:
            raise Exception(
                "Ano fora do limite" "O ano " + str(ano) + " nao esta no limite determinado nas configuracoes")

    def printTabelas(self, tabelaDosAnos, tabelaDosTipos):
        print "\n**************************************************\n"
        print "\nTABELAS DOS QUALIS:\n\n"

        for i in range(len(tabelaDosAnos)):
            print str(self.anoInicio + i) + ":"
            print "------"
            print tabelaDosAnos[i]
            print "\n\n"

        print "\nTOTAIS POR TIPO:\n"
        print tabelaDosTipos
        print "\n\n"

        parar()

    def calcularTotaisDosQualis(self, grupo):

        # if (not grupo.obterParametro('global-arquivo_qualis_de_periodicos')==''):
        # self.qtdPB0 = self.calcularTotaisDosQualisPorTipo(self.qtdPB0, grupo.compilador.listaCompletaArtigoEmPeriodico)

        if not grupo.obterParametro('global-arquivo_qualis_de_congressos') == '':
            self.qtdPB4 = calcularTotaisDosQualisPorTipo(self.qtdPB4,
                                                         grupo.compilador.listaCompletaTrabalhoCompletoEmCongresso)
            self.qtdPB5 = calcularTotaisDosQualisPorTipo(self.qtdPB5,
                                                         grupo.compilador.listaCompletaResumoExpandidoEmCongresso)

    def buscaQualis(self, tipo, nome):
        dist = 0
        indice = 0
        # Percorrer lista de periodicos tentando casar com nome usando funcao compararCadeias(str1, str2) de scriptLattes.py
        if tipo == 'P':
            if self.periodicos.get(nome) is not None:
                return self.periodicos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
            else:
                chaves = self.periodicos.keys()
                for i in range(0, len(chaves)):
                    distI = compararCadeias(nome, chaves[i], qualis=True)
                    if distI > dist:  # comparamos: nome com cada nome de periodico
                        indice = i
                        dist = distI
                if indice > 0:
                    return self.periodicos.get(chaves[indice]), chaves[indice]  # Retorna Qualis de nome similar
            return None, None
        else:
            if self.congressos.get(nome) is not None:
                return self.congressos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
            else:
                chaves = self.congressos.keys()
                for i in range(0, len(chaves)):
                    distI = compararCadeias(nome, chaves[i], qualis=True)
                    if distI > dist:  # comparamos: nome com cada nome de evento
                        indice = i
                        dist = distI
                if indice > 0:
                    return self.congressos.get(chaves[indice]), chaves[indice]  # Retorna Qualis de nome similar
        # return 'Qualis nao identificado', ''
        return 'Qualis nao identificado', nome

    def analisarPublicacoes(self, membro, grupo):
        # Percorrer lista de publicacoes buscando e contabilizando os qualis
        for pub in membro.listaArtigoEmPeriodico:
            # qualis, similar = self.buscaQualis('P', pub.revista)
            # pub.qualis = qualis
            qualis = self.qextractor.get_qualis_by_issn(pub.issn)
            if pub.issn and qualis:
                pub.qualis = qualis
            # FIXME: utilizaria o comportamento antigo (ler qualis de um CSV), mas nao funciona se nao a configuracao global-arquivo_qualis_de_periodicos nao for definida
            # elif not self.extrair_qualis_online:
            #     qualis, similar = self.buscaQualis('P', pub.revista)
            #     pub.qualis = qualis
            #     pub.qualissimilar = similar
            else:
                pub.qualis = None
                pub.qualissimilar = None

        if not grupo.obterParametro('global-arquivo_qualis_de_congressos') == '':
            for pub in membro.listaTrabalhoCompletoEmCongresso:
                qualis, similar = self.buscaQualis('C', pub.nomeDoEvento)
                if qualis == 'Qualis nao identificado':
                    if self.congressos.get(pub.sigla) is not None:
                        qualis = self.congressos.get(pub.sigla)  # Retorna Qualis da sigla com nome do evento
                        similar = pub.sigla
                    else:
                        qualis = 'Qualis nao identificado'
                        similar = pub.nomeDoEvento
                pub.qualis = qualis
                pub.qualissimilar = similar

            for pub in membro.listaResumoExpandidoEmCongresso:
                qualis, similar = self.buscaQualis('C', pub.nomeDoEvento)
                pub.qualis = qualis
                pub.qualissimilar = similar
