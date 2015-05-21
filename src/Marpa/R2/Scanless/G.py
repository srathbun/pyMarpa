# Copyright 2015 Jeffrey Kegler
# This file is part of Marpa.R2.  Marpa.R2 is free software: you can
# redistribute it and/or modify it under the terms of the GNU Lesser
# General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Marpa.R2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public License along with Marpa.R2.  If not, see
# http://www.gnu.org/licenses/.

# package Marpa.R2.Scanless.G

import Internal.Scanless.G

VERSION = '3.001_000'

def new(class, hash_ref_args):
    slg = []

    dsl, g1_args = Internal.Scanless.G.set(slg, 'new', hash_ref_args)
    ast = Internal.MetaAST.new(dsl)
    hashed_ast = ast.ast_to_hash()
    Internal.Scanless.G.hash_to_runtime(slg, hashed_ast, g1_args)
    return slg

def set(slg, hash_ref_args):
    Internal.Scanless.G.set(slg, 'set', hash_ref_args)
    return slg

def thick_defgrammar_by_name(slg, defgrammar='G1'):
    # Allow G0 as legacy synonym for L0
    grammar_names = { 'G0' => 1, 'G1' => 1, 'L0' => 1 }

	if not grammar_names[defgrammar]:
		raise Exception('No lexer named "{0}"'.format(defgrammar))

	if defgrammar == 'G1':
		return slg[Internal.Scanless.G.THICK_G1_GRAMMAR]
	else:
		return slg[Internal.Scanless.G.THICK_LEX_GRAMMARS][0]

def start_symbol_id(slg, rule_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).start_symbol()

def rule_name(slg, rule_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).rule_name(rule_id)

def rule_expand(slg, rule_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).tracer()
        .rule_expand(rule_id)

def symbol_name(slg, symbol_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).tracer()
        .symbol_name(symbol_id)

def symbol_display_form(slg, symbol_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar)
        .symbol_in_display_form(symbol_id)

def symbol_dsl_form(slg, symbol_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar)
        .symbol_dsl_form(symbol_id)

def symbol_description(slg, symbol_id, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar)
        .symbol_description(symbol_id)

def rule_show(slg, rule_id, defgrammar):
    return slg_rule_show(slg, rule_id, thick_defgrammar_by_name(slg, defgrammar))

def slg_rule_show(slg, rule_id, defgrammar):
    tracer       = defgrammar.tracer()
    defgrammar_c = defgrammar[Internal.Grammar.C]
    symbol_ids   = tracer.rule_expand(rule_id)
	if isinstance(symbol_ids, basestring):
		return symbol_ids
    rhs = map(defgrammar.symbol_in_display_form, symbol_ids)
	lhs = rhs[0]
	rhs = rhs[1:]
    minimum    = defgrammar_c.sequence_min(rule_id)
    quantifier = ''

    if minimum:
        quantifier = '*' if minimum <= 0 else '+'
    return "".join([lhs, '.=', rhs, quantifier])

def show_rules(slg, verbose=0, defgrammar='G1'):
    text = ""
    thick_grammar = thick_defgrammar_by_name(slg, defgrammar)
    rules     = thick_grammar[Internal.Grammar.RULES]
    grammar_c = thick_grammar[Internal.Grammar.C]

	for rule in rules:
        rule_id = rule[Internal.Rule.ID]

        minimum = grammar_c.sequence_min(rule_id)
		if minimum:
			quantifier = '*' if minimum <= 0 else '+'
		else:
			quantifier = ''
        lhs_id      = grammar_c.rule_lhs(rule_id)
        rule_length = grammar_c.rule_length(rule_id)
        rhs_ids = []
		for r in range(0, len(rule_length)-1):
            rhs_ids.push(grammar_c.rule_rhs(rule_id, r))

        text = text + ' '.join([defgrammar, "Rrule_id",
            thick_grammar.symbol_in_display_form(lhs_id),
            '.=',
            map(thick_grammar.symbol_in_display_form, rhs_ids),
            quantifier])
        text = text + "\n"

        if verbose >= 2:
            description = rule[Internal.Rule.DESCRIPTION]
			if description:
				text = text + "  description\n"
            comment = []
			if grammar_c.rule_length(rule_id) == 0:
                comment.push('empty')
			if not thick_grammar.rule_is_used(rule_id):
                comment.push('!used')
			if not grammar_c.rule_is_productive(rule_id):
                comment.push('unproductive')
			if not grammar_c.rule_is_accessible(rule_id):
				comment.push('inaccessible')
			if rule[Internal.Rule.DISCARD_SEPARATION]:
                comment.push('discard_sep')

			if comment:
                text = text +
					' ' + ' '.join('/*', comment, '*/') + "\n"

            text = text + "  Symbol IDs: <lhs_id> .= " +
				' '.join(map(lambda x: "<" + x +">", rhs_ids)) + "\n"

		if verbose >= 3:
            tracer = thick_grammar.tracer()
            text = text + "  Internal symbols: <" +
                tracer.symbol_name(lhs_id) +
                '> .= ' + ' '.join(
					map(lambda x: '<' + tracer.symbol_name(x) + '>', rhs_ids)
                ) + "\n"

    return text

def show_symbols(slg, verbose=0, defgrammar='G1'):
	text = ''

    thick_grammar = thick_defgrammar_by_name(slg, defgrammar)

    symbols   = thick_grammar[Internal.Grammar.SYMBOLS]
    grammar_c = thick_grammar[Internal.Grammar.C]

    for symbol in symbols:
        symbol_id = symbol[Internal.Symbol.ID]

        text = text + ' '.join([defgrammar, "Ssymbol_id",
            thick_grammar.symbol_in_display_form(symbol_id)])

        description = symbol[Internal.Symbol.DESCRIPTION]
		if description:
            text = text + " -- description"
        text =  text + "\n"

		if verbose >= 2:
            tag_list = []
			if not grammar_c.symbol_is_productive(symbol_id):
                tag_list.push('unproductive')
			if not grammar_c.symbol_is_accessible(symbol_id):
                tag_list.push('inaccessible')
			if grammar_c.symbol_is_nulling(symbol_id):
                tag_list.push('nulling')
			if grammar_c.symbol_is_terminal(symbol_id):
                tag_list.push('terminal')

			if tag_list:
                text = text +
                    ' ' + ' '.join('/*', tag_list, '*/') + "\n"

            tracer = thick_grammar.tracer()
            text = text + "  Internal name: <" +
                tracer.symbol_name(symbol_id) + ">\n"

		if verbose >= 3:
            dsl_form = symbol[Internal.Symbol.DSL_FORM]
			if dsl_form:
				text = text + "SLIF name: {0}\n".format(dsl_form)

    return text

def show_dotted_rule(slg, rule_id, dot_position):
    grammar =  slg[Internal.Scanless.G.THICK_G1_GRAMMAR]
    tracer  = grammar.tracer()
    grammar_c = grammar[Internal.Grammar.C]
	rhs = map(grammar.symbol_in_display_form, tracer.rule_expand(rule_id))
	lhs = rhs.pop(0)
    rhs_length = len(rhs)

    minimum = grammar_c.sequence_min(rule_id)
    quantifier = []
	if minimum:
        quantifier = '*' if minimum <= 0 else '+'
	if dot_position < 0:
		dot_position = 0
	if dot_position < rhs_length:
        rhs[dot_position] = '.'
        return ''.join([' ', lhs, '.', rhs, quantifier])
    else:
        return ''.join([' ', lhs, '.', rhs, quantifier, '.'])

def rule(slg, args):
    return slg[Internal.Scanless.G.THICK_G1_GRAMMAR]
        .rule(args)

def rule_ids(slg, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).rule_ids()

def symbol_ids(slg, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).symbol_ids()

def g1_rule_ids(slg):
    return slg.rule_ids()

def g0_rule_ids(slg):
	return slg.rule_ids('L0')

def g0_rule(slg, args):
    return slg[Internal.Scanless.G.THICK_LEX_GRAMMARS][0]
        .rule(args)

# Internal methods, not to be documented

def thick_g1_grammar(slg):
    return slg[Internal.Scanless.G.THICK_G1_GRAMMAR]

def show_irls(slg, defgrammar):
    return thick_defgrammar_by_name(slg, defgrammar).show_irls()
