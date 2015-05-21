# Copyright 2015 Jeffrey Kegler
# This file is part of Marpa::R2.  Marpa::R2 is free software: you can
# redistribute it and/or modify it under the terms of the GNU Lesser
# General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Marpa::R2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public License along with Marpa::R2.  If not, see
# http://www.gnu.org/licenses/.

# package Marpa::R2::Scanless::G;

VERSION = '3.001_000'

sub Marpa::R2::Scanless::G::new {
    my ( $class, @hash_ref_args ) = @_;

    my $slg = [];
    bless $slg, $class;

    my ($dsl, $g1_args) = Marpa::R2::Internal::Scanless::G::set ( $slg, 'new', @hash_ref_args );
    my $ast = Marpa::R2::Internal::MetaAST->new( $dsl );
    my $hashed_ast = $ast->ast_to_hash();
    Marpa::R2::Internal::Scanless::G::hash_to_runtime($slg, $hashed_ast, $g1_args);
    return $slg;
} ## end sub Marpa::R2::Scanless::G::new

sub Marpa::R2::Scanless::G::set {
    my ( $slg, @hash_ref_args ) = @_;
    Marpa::R2::Internal::Scanless::G::set ( $slg, 'set', @hash_ref_args );
    return $slg;
}

sub thick_subgrammar_by_name {
    my ( $slg, $subgrammar ) = @_;

    # Allow G0 as legacy synonym for L0
    state $grammar_names = { 'G0' => 1, 'G1' => 1, 'L0' => 1 };
    $subgrammar //= 'G1';

    Marpa::R2::exception(qq{No lexer named "$subgrammar"})
        if not defined $grammar_names->{$subgrammar};

    return $slg->[Marpa::R2::Internal::Scanless::G::THICK_G1_GRAMMAR]
        if $subgrammar eq 'G1';

    return $slg->[Marpa::R2::Internal::Scanless::G::THICK_LEX_GRAMMARS]
        ->[0];
} ## end sub thick_subgrammar_by_name

sub Marpa::R2::Scanless::G::start_symbol_id {
    my ( $slg, $rule_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name( $slg, $subgrammar )->start_symbol();
}

sub Marpa::R2::Scanless::G::rule_name {
    my ( $slg, $rule_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name( $slg, $subgrammar )->rule_name($rule_id);
}

sub Marpa::R2::Scanless::G::rule_expand {
    my ( $slg, $rule_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name( $slg, $subgrammar )->tracer()
        ->rule_expand($rule_id);
}

sub Marpa::R2::Scanless::G::symbol_name {
    my ( $slg, $symbol_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name($slg, $subgrammar)->tracer()
        ->symbol_name($symbol_id);
}

sub Marpa::R2::Scanless::G::symbol_display_form {
    my ( $slg, $symbol_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name( $slg, $subgrammar )
        ->symbol_in_display_form($symbol_id);
}

sub Marpa::R2::Scanless::G::symbol_dsl_form {
    my ( $slg, $symbol_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name( $slg, $subgrammar )
        ->symbol_dsl_form($symbol_id);
}

sub Marpa::R2::Scanless::G::symbol_description {
    my ( $slg, $symbol_id, $subgrammar ) = @_;
    return thick_subgrammar_by_name($slg, $subgrammar)
        ->symbol_description($symbol_id);
}

sub Marpa::R2::Scanless::G::rule_show
{
    my ( $slg, $rule_id, $subgrammar) = @_;
    return slg_rule_show($slg, $rule_id, thick_subgrammar_by_name($slg, $subgrammar));
}

sub slg_rule_show {
    my ( $slg, $rule_id, $subgrammar ) = @_;
    my $tracer       = $subgrammar->tracer();
    my $subgrammar_c = $subgrammar->[Marpa::R2::Internal::Grammar::C];
    my @symbol_ids   = $tracer->rule_expand($rule_id);
    return if not scalar @symbol_ids;
    my ( $lhs, @rhs ) =
        map { $subgrammar->symbol_in_display_form($_) } @symbol_ids;
    my $minimum    = $subgrammar_c->sequence_min($rule_id);
    my @quantifier = ();

    if ( defined $minimum ) {
        @quantifier = ( $minimum <= 0 ? q{*} : q{+} );
    }
    return join q{ }, $lhs, q{::=}, @rhs, @quantifier;
} ## end sub slg_rule_show

sub Marpa::R2::Scanless::G::show_rules {
    my ( $slg, $verbose, $subgrammar ) = @_;
    my $text     = q{};
    $verbose    //= 0;
    $subgrammar //= 'G1';

    my $thick_grammar = thick_subgrammar_by_name($slg, $subgrammar);

    my $rules     = $thick_grammar->[Marpa::R2::Internal::Grammar::RULES];
    my $grammar_c = $thick_grammar->[Marpa::R2::Internal::Grammar::C];

    for my $rule ( @{$rules} ) {
        my $rule_id = $rule->[Marpa::R2::Internal::Rule::ID];

        my $minimum = $grammar_c->sequence_min($rule_id);
        my @quantifier =
            defined $minimum ? $minimum <= 0 ? (q{*}) : (q{+}) : ();
        my $lhs_id      = $grammar_c->rule_lhs($rule_id);
        my $rule_length = $grammar_c->rule_length($rule_id);
        my @rhs_ids =
            map { $grammar_c->rule_rhs( $rule_id, $_ ) }
            ( 0 .. $rule_length - 1 );
        $text .= join q{ }, $subgrammar, "R$rule_id",
            $thick_grammar->symbol_in_display_form($lhs_id),
            '::=',
            ( map { $thick_grammar->symbol_in_display_form($_) } @rhs_ids ),
            @quantifier;
        $text .= "\n";

        if ( $verbose >= 2 ) {

            my $description = $rule->[Marpa::R2::Internal::Rule::DESCRIPTION];
            $text .= "  $description\n" if $description;
            my @comment = ();
            $grammar_c->rule_length($rule_id) == 0
                and push @comment, 'empty';
            $thick_grammar->rule_is_used($rule_id)
                or push @comment, '!used';
            $grammar_c->rule_is_productive($rule_id)
                or push @comment, 'unproductive';
            $grammar_c->rule_is_accessible($rule_id)
                or push @comment, 'inaccessible';
            $rule->[Marpa::R2::Internal::Rule::DISCARD_SEPARATION]
                and push @comment, 'discard_sep';

            if (@comment) {
                $text .= q{  } . ( join q{ }, q{/*}, @comment, q{*/} ) . "\n";
            }

            $text .= "  Symbol IDs: <$lhs_id> ::= "
                . ( join q{ }, map {"<$_>"} @rhs_ids ) . "\n";

        } ## end if ( $verbose >= 2 )

        if ( $verbose >= 3 ) {

            my $tracer = $thick_grammar->tracer();

            $text
                .= "  Internal symbols: <"
                . $tracer->symbol_name($lhs_id)
                . q{> ::= }
                . (
                join q{ },
                map { '<' . $tracer->symbol_name($_) . '>' } @rhs_ids
                ) . "\n";

        } ## end if ( $verbose >= 3 )

    } ## end for my $rule ( @{$rules} )

    return $text;
} ## end sub Marpa::R2::Scanless::G::show_rules

sub Marpa::R2::Scanless::G::show_symbols {
    my ( $slg, $verbose, $subgrammar ) = @_;
    my $text = q{};
    $verbose    //= 0;
    $subgrammar //= 'G1';

    my $thick_grammar = thick_subgrammar_by_name($slg, $subgrammar);

    my $symbols   = $thick_grammar->[Marpa::R2::Internal::Grammar::SYMBOLS];
    my $grammar_c = $thick_grammar->[Marpa::R2::Internal::Grammar::C];

    for my $symbol ( @{$symbols} ) {
        my $symbol_id = $symbol->[Marpa::R2::Internal::Symbol::ID];

        $text .= join q{ }, $subgrammar, "S$symbol_id",
            $thick_grammar->symbol_in_display_form($symbol_id);

        my $description = $symbol->[Marpa::R2::Internal::Symbol::DESCRIPTION];
        if ($description) {
            $text .= " -- $description";
        }
        $text .= "\n";

        if ( $verbose >= 2 ) {

            my @tag_list = ();
            $grammar_c->symbol_is_productive($symbol_id)
                or push @tag_list, 'unproductive';
            $grammar_c->symbol_is_accessible($symbol_id)
                or push @tag_list, 'inaccessible';
            $grammar_c->symbol_is_nulling($symbol_id)
                and push @tag_list, 'nulling';
            $grammar_c->symbol_is_terminal($symbol_id)
                and push @tag_list, 'terminal';

            if (@tag_list) {
                $text
                    .= q{  } . ( join q{ }, q{/*}, @tag_list, q{*/} ) . "\n";
            }

            my $tracer = $thick_grammar->tracer();
            $text .= "  Internal name: <"
                . $tracer->symbol_name($symbol_id) . qq{>\n};

        } ## end if ( $verbose >= 2 )

        if ( $verbose >= 3 ) {

            my $dsl_form = $symbol->[Marpa::R2::Internal::Symbol::DSL_FORM];
            if ($dsl_form) { $text .= qq{  SLIF name: $dsl_form\n}; }

        } ## end if ( $verbose >= 3 )

    } ## end for my $symbol ( @{$symbols} )

    return $text;
} ## end sub Marpa::R2::Scanless::G::show_symbols

sub Marpa::R2::Scanless::G::show_dotted_rule {
    my ( $slg, $rule_id, $dot_position ) = @_;
    my $grammar =  $slg->[Marpa::R2::Internal::Scanless::G::THICK_G1_GRAMMAR];
    my $tracer  = $grammar->tracer();
    my $grammar_c = $grammar->[Marpa::R2::Internal::Grammar::C];
    my ( $lhs, @rhs ) =
    map { $grammar->symbol_in_display_form($_) } $tracer->rule_expand($rule_id);
    my $rhs_length = scalar @rhs;

    my $minimum = $grammar_c->sequence_min($rule_id);
    my @quantifier = ();
    if (defined $minimum) {
        @quantifier = ($minimum <= 0 ? q{*} : q{+} );
    }
    $dot_position = 0 if $dot_position < 0;
    if ($dot_position < $rhs_length) {
        splice @rhs, $dot_position, 0, q{.};
        return join q{ }, $lhs, q{->}, @rhs, @quantifier;
    } else {
        return join q{ }, $lhs, q{->}, @rhs, @quantifier, q{.};
    }
} ## end sub Marpa::R2::Grammar::show_dotted_rule

sub Marpa::R2::Scanless::G::rule {
    my ( $slg, @args ) = @_;
    return $slg->[Marpa::R2::Internal::Scanless::G::THICK_G1_GRAMMAR]
        ->rule(@args);
}

sub Marpa::R2::Scanless::G::rule_ids {
    my ($slg, $subgrammar) = @_;
    return thick_subgrammar_by_name($slg, $subgrammar)->rule_ids();
}

sub Marpa::R2::Scanless::G::symbol_ids {
    my ($slg, $subgrammar) = @_;
    return thick_subgrammar_by_name($slg, $subgrammar)->symbol_ids();
}

sub Marpa::R2::Scanless::G::g1_rule_ids {
    my ($slg) = @_;
    return $slg->rule_ids();
}

sub Marpa::R2::Scanless::G::g0_rule_ids {
    my ($slg) = @_;
    return $slg->rule_ids('L0');
}

sub Marpa::R2::Scanless::G::g0_rule {
    my ( $slg, @args ) = @_;
    return $slg->[Marpa::R2::Internal::Scanless::G::THICK_LEX_GRAMMARS]->[0]
        ->rule(@args);
}

# Internal methods, not to be documented

sub Marpa::R2::Scanless::G::thick_g1_grammar {
    my ($slg) = @_;
    return $slg->[Marpa::R2::Internal::Scanless::G::THICK_G1_GRAMMAR];
}

sub Marpa::R2::Scanless::G::show_irls {
    my ($slg, $subgrammar) = @_;
    return thick_subgrammar_by_name($slg, $subgrammar)->show_irls();
}
