from codecs import replace_errors
from curses import window
from distutils.log import error
from logging import warning
from time import time

from numpy import number # For time
from strings_with_arrows import * # External source
import string
import os # Should be installed by default
import os.path
import math
import time
import webbrowser # For web functions
import turtle # Not needed in factory-set VKode
from urllib import request
from pathlib import Path # For paths
from urllib.request import urlopen
import requests
from datetime import datetime
import pymsgbox # For dialogue windows
import subprocess
from colorama import init # For colored text lines
init() # Initiate Colorama (from line 17)
from colorama import Fore, Back, Style # And finally importing Colorama (from line 17)
from inspect import currentframe, getframeinfo # Library needed to get information to warnings


# CONSTANTS
DIGITS = '0123456789' # Numbers
LETTERS = string.ascii_letters # Letters
LETTERS_DIGITS = LETTERS + DIGITS # Numbers and letters :)

vkode_location = os.path.abspath(__file__) # Getting vkode.py location
vkode_location = vkode_location[:-8] # Deleting the 'vkode.py' in the end of the vkode.py location (from line 28)
global frameinfo
frameinfo = getframeinfo(currentframe()) # Info about current file and current line
actual_location = ""

global openedfile
openedfile = ""
global runloc
runloc = ""

debugl = Fore.YELLOW + ">>> " + Fore.RESET




# WARNINGS
global warning_sign
warning_sign = Fore.RED + "  ! " + Fore.RESET
global frame_info
frame_info = ""

def warning_set():
  global frameinfo
  global warning_sign
  global runloc
  actual_location = frameinfo.filename
  warning_sign = warning_sign + Style.BRIGHT + "VKODE WARNING!" + Style.DIM + " The program will probably continue running after printing following warning message." + "\n    " + "VKode warning: Issue was found by " + actual_location.replace("\\", "/") + " line " + str(frameinfo.lineno) + "\n    " + "locationRun() = " + runloc + "\n    " + Style.BRIGHT
    


# ERRORS
class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details
  
  def as_string(self):
    result  = f'{self.error_name}: {self.details}\n'
    result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details=''):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

  def generate_traceback(self):
    result = ''
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return 'Traceback (most recent call last):\n' + result


# position

class Position:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt

  def advance(self, current_char=None):
    self.idx += 1
    self.col += 1

    if current_char == '\n':
      self.ln += 1
      self.col = 0

    return self

  def copy(self):
    return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


# tokens

TT_INT				= 'INT'
TT_FLOAT    	= 'FLOAT'
TT_STRING			= 'STRING'
TT_IDENTIFIER	= 'IDENTIFIER'
TT_KEYWORD		= 'KEYWORD'
TT_PLUS     	= 'PLUS'
TT_MINUS    	= 'MINUS'
TT_MUL      	= 'MUL'
TT_DIV      	= 'DIV'
TT_POW				= 'POW'
TT_EQ					= 'EQ'
TT_LPAREN   	= 'LPAREN'
TT_RPAREN   	= 'RPAREN'
TT_LSQUARE    = 'LSQUARE'
TT_RSQUARE    = 'RSQUARE'
TT_EE					= 'EE'
TT_NE					= 'NE'
TT_LT					= 'LT'
TT_GT					= 'GT'
TT_LTE				= 'LTE'
TT_GTE				= 'GTE'
TT_COMMA			= 'COMMA'
TT_ARROW			= 'ARROW'
TT_NEWLINE		= 'NEWLINE'
TT_EOF				= 'EOF'

KEYWORDS = [
  'VAR',
  'AND',
  'OR',
  'NOT',
  'IF',
  'ELIF',
  'ELSE',
  'FOR',
  'TO',
  'STEP',
  'WHILE',
  'FUN',
  'THEN',
  'END',
  'RETURN',
  'CONTINUE',
  'BREAK',
]

class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value

    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  def matches(self, type_, value):
    return self.type == type_ and self.value == value
  
  def __repr__(self):
    if self.value: return f'{self.type}:{self.value}'
    return f'{self.type}'


# LEXER


class Lexer:
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()
  
  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  def make_tokens(self):
    tokens = []

    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char == '#':
        self.skip_comment()
      elif self.current_char in ';\n':
        tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
        self.advance()
      elif self.current_char in DIGITS:
        tokens.append(self.make_number())
      elif self.current_char in LETTERS:
        tokens.append(self.make_identifier())
      elif self.current_char == '"':
        tokens.append(self.make_string())
      elif self.current_char == '+':
        tokens.append(Token(TT_PLUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(self.make_minus_or_arrow())
      elif self.current_char == '*':
        tokens.append(Token(TT_MUL, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(Token(TT_DIV, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(Token(TT_POW, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(Token(TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(Token(TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '[':
        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == ']':
        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '!':
        token, error = self.make_not_equals()
        if error: return [], error
        tokens.append(token)
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ',':
        tokens.append(Token(TT_COMMA, pos_start=self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(Token(TT_EOF, pos_start=self.pos))
    return tokens, None

  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in DIGITS + '.':
      if self.current_char == '.':
        if dot_count == 1: break
        dot_count += 1
      num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return Token(TT_INT, int(num_str), pos_start, self.pos)
    else:
      return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

  def make_string(self):
    string = ''
    pos_start = self.pos.copy()
    escape_character = False
    self.advance()

    escape_characters = {
      'n': '\n',
      't': '\t'
    }

    while self.current_char != None and (self.current_char != '"' or escape_character):
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
        else:
          string += self.current_char
      self.advance()
      escape_character = False
    
    self.advance()
    return Token(TT_STRING, string, pos_start, self.pos)

  def make_identifier(self):
    id_str = ''
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
      id_str += self.current_char
      self.advance()

    tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
    return Token(tok_type, id_str, pos_start, self.pos)

  def make_minus_or_arrow(self):
    tok_type = TT_MINUS
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '>':
      self.advance()
      tok_type = TT_ARROW

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")
  
  def make_equals(self):
    tok_type = TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_EE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_less_than(self):
    tok_type = TT_LT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_LTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_greater_than(self):
    tok_type = TT_GT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_GTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def skip_comment(self):
    self.advance()

    while self.current_char != '\n':
      self.advance()

    self.advance()


# nodes

class NumberNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class StringNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes

    self.pos_start = pos_start
    self.pos_end = pos_end

class VarAccessNode:
  def __init__(self, var_name_tok):
    self.var_name_tok = var_name_tok

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

class BinOpNode:
  def __init__(self, left_node, op_tok, right_node):
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f'({self.op_tok}, {self.node})'

class IfNode:
  def __init__(self, cases, else_case):
    self.cases = cases
    self.else_case = else_case

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

class ForNode:
  def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
    self.var_name_tok = var_name_tok
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.step_value_node = step_value_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.body_node.pos_end

class WhileNode:
  def __init__(self, condition_node, body_node, should_return_null):
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

class FuncDefNode:
  def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.should_auto_return = should_auto_return

    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(self.arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

class CallNode:
  def __init__(self, node_to_call, arg_nodes):
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes

    self.pos_start = self.node_to_call.pos_start

    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end

class ContinueNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end

class BreakNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end


# parse results

class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self


# parser

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()

  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]

  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res

  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    while self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      newline_count = 0
      while self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False
      
      if not more_statements: break
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.matches(TT_KEYWORD, 'RETURN'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
    
    if self.current_tok.matches(TT_KEYWORD, 'CONTINUE'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
      
    if self.current_tok.matches(TT_KEYWORD, 'BREAK'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
      ))
    return res.success(expr)

  def expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'VAR'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected identifier"
        ))

      var_name = self.current_tok
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected '='"
        ))

      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      return res.success(VarAssignNode(var_name, expr))

    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'AND'), (TT_KEYWORD, 'OR'))))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
      ))

    return res.success(node)

  def comp_expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'NOT'):
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res
      return res.success(UnaryOpNode(op_tok, node))
    
    node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
    
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN' or 'NOT'"
      ))

    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

  def term(self):
    return self.bin_op(self.factor, (TT_MUL, TT_DIV))

  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_PLUS, TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def power(self):
    return self.bin_op(self.call, (TT_POW, ), self.factor)

  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      arg_nodes = []

      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        if self.current_tok.type != TT_RPAREN:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ')'"
          ))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  def atom(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_INT, TT_FLOAT):
      res.register_advancement()
      self.advance()
      return res.success(NumberNode(tok))

    elif tok.type == TT_STRING:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    elif tok.type == TT_IDENTIFIER:
      res.register_advancement()
      self.advance()
      return res.success(VarAccessNode(tok))

    elif tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ')'"
        ))

    elif tok.type == TT_LSQUARE:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)
    
    elif tok.matches(TT_KEYWORD, 'IF'):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    elif tok.matches(TT_KEYWORD, 'FOR'):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    elif tok.matches(TT_KEYWORD, 'WHILE'):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)

    elif tok.matches(TT_KEYWORD, 'FUN'):
      func_def = res.register(self.func_def())
      if res.error: return res
      return res.success(func_def)

    return res.failure(InvalidSyntaxError(
      tok.pos_start, tok.pos_end,
      "Expected int, float, identifier, '+', '-', '(', '[', IF', 'FOR', 'WHILE', 'FUN'"
    ))

  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_RSQUARE:
      res.register_advancement()
      self.advance()
    else:
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
        ))

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ']'"
        ))

      res.register_advancement()
      self.advance()

    return res.success(ListNode(
      element_nodes,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('IF'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  def if_expr_b(self):
    return self.if_expr_cases('ELIF')
    
  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_tok.matches(TT_KEYWORD, 'END'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'END'"
          ))
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    if self.current_tok.matches(TT_KEYWORD, 'ELIF'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res
    
    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_tok.matches(TT_KEYWORD, 'END'):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))

  def for_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'FOR'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))

    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_EQ:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '='"
      ))
    
    res.register_advancement()
    self.advance()

    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'TO'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'TO'"
      ))
    
    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    if self.current_tok.matches(TT_KEYWORD, 'STEP'):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res
    else:
      step_value = None

    if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'END'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'END'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

  def while_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'WHILE'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'END'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'END'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

  def func_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'FUN'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'FUN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else:
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or '('"
        ))
    
    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()
      
      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()
      
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else:
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))
    
    if self.current_tok.type != TT_NEWLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or NEWLINE"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'END'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'END'"
      ))

    res.register_advancement()
    self.advance()
    
    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      False
    ))

  ###################################

  def bin_op(self, func_a, ops, func_b=None):
    if func_b == None:
      func_b = func_a
    
    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()
      right = res.register(func_b())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)

    return res.success(left)


# runtime result

class RTResult:
  def __init__(self):
    self.reset()

  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self
  
  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    return (
      self.error or
      self.func_return_value or
      self.loop_should_continue or
      self.loop_should_break
    )


# values

class Value:
  def __init__(self):
    self.set_pos()
    self.set_context()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context=None):
    self.context = context
    return self

  def added_to(self, other):
    return None, self.illegal_operation(other)

  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  def multed_by(self, other):
    return None, self.illegal_operation(other)

  def dived_by(self, other):
    return None, self.illegal_operation(other)

  def powed_by(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  def anded_by(self, other):
    return None, self.illegal_operation(other)

  def ored_by(self, other):
    return None, self.illegal_operation(other)

  def notted(self, other):
    return None, self.illegal_operation(other)

  def execute(self, args):
    return RTResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def is_true(self):
    return False

  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(
      self.pos_start, other.pos_end,
      'Illegal operation',
      self.context
    )

class Number(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)
  
  def __repr__(self):
    return str(self.value)

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)

class String(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def is_true(self):
    return len(self.value) > 0

  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return self.value

  def __repr__(self):
    return f'"{self.value}"'

class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be removed from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)
  
  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return ", ".join([str(x) for x in self.elements])

  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.elements])}]'

class BaseFunction(Value):
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  def check_args(self, arg_names, args):
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(args) - len(arg_names)} too many args passed into {self}",
        self.context
      ))
    
    if len(args) < len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(arg_names) - len(args)} too few args passed into {self}",
        self.context
      ))

    return res.success(None)

  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_table.set(arg_name, arg_value)

  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = RTResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return(): return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)

class Function(BaseFunction):
  def __init__(self, name, body_node, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  def execute(self, args):
    res = RTResult()
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(ret_value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RTResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)
  
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"

  #####################################

  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RTResult().success(Number.null)
  execute_print.arg_names = ['value']

  global entcolor
  entcolor = 0

  def execute_printstyle(self, exec_ctx):
    global entcolor
    colorstring = (str(exec_ctx.symbol_table.get('value')))
    if entcolor == 0:
      print(colorstring)
    if entcolor == 1:
      print(Fore.RED + colorstring + Style.RESET_ALL)
    if entcolor == 2:
      print(Fore.GREEN + colorstring + Style.RESET_ALL)
    if entcolor == 3:
      print(Fore.BLUE + colorstring + Style.RESET_ALL)
    return RTResult().success(Number.null)
  execute_printstyle.arg_names = ['value']

  def execute_printstyleSetcolor(self, exec_ctx):
    global entcolor
    setcolored = (str(exec_ctx.symbol_table.get('value')))
    if setcolored == "red":
      entcolor = 1
    if setcolored == "green":
      entcolor = 2
    if setcolored == "blue":
      entcolor = 3
    if setcolored == "/clear/":
      entcolor = 0
    if setcolored == "white":
      entcolor = 0
    return RTResult().success(Number.null)
  execute_printstyleSetcolor.arg_names = ['value']

  def execute_style(self, exec_ctx):
    stylevalue = (str(exec_ctx.symbol_table.get('value')))
    if stylevalue == "red":
      print(Fore.RED)
    if stylevalue == "green":
      print(Fore.GREEN)
    if stylevalue == "blue":
      print(Fore.BLUE)
    if stylevalue == "/clear/":
      print(Style.RESET_ALL)
    if stylevalue == "white":
      print(Style.RESET_ALL)
    return RTResult().success(Number.null)
  execute_style.arg_names = ['value']
  
  def execute_print_ret(self, exec_ctx):
    return RTResult().successF(String(str(exec_ctx.symbol_table.get('value'))))
  execute_print_ret.arg_names = ['value']

  def execute_kill(self, exec_ctx):
    return RTResult().success(print("  > Killing console..."), exit())
  execute_kill.arg_names = []

  def execute_readfile(self, exec_ctx):
    openfilelocation = str(exec_ctx.symbol_table.get('value'))
    fread_f = open(openfilelocation, "r")
    fread = fread_f.read()
    return RTResult().success(String(fread))
  execute_readfile.arg_names = ['value']

  def execute_time(self, exec_ctx):
    cas = datetime.now()
    cas = (cas)
    return RTResult().success(Number(cas))
  execute_time.arg_names = []

  def execute_file(self, exec_ctx):
    openapplocation = str(exec_ctx.symbol_table.get('value'))
    os.startfile(openapplocation)
    return RTResult().success(Number.null)
  execute_file.arg_names = ['value']

  def execute_tacet(self, exec_ctx):
    sleeptime = str(exec_ctx.symbol_table.get('number'))
    timesleeping = int(sleeptime)
    time.sleep(timesleeping)
    return RTResult().success(Number.null)
  execute_tacet.arg_names = ['number']

  def execute_use(self, exec_ctx):
    use = str(exec_ctx.symbol_table.get('value'))
    move_f = open(vkode_location + "libs.saver", "r")
    move = move_f.read()
    #print(move)
    move_f.close()
    if use in move:
      call = "lib\\" + use + "\\" + use + ".py"
      subprocess.call(call, shell=True)
    else:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "Library with name " + use + " (" + vkode_location.replace("\\", "/") + "lib/" + use + "/" + use + ".py)" + " is not on the library list (libs.saver)." + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
              
    return RTResult().success(Number.null)
  execute_use.arg_names = ['value']
  
  def execute_devview(self, exec_ctx):
    #os.startfile("devview/devv4.py – zastupce")
    #subprocess.call('start /wait python devview/devv4.py', shell=True)
    return RTResult().success(Number.null)
  execute_devview.arg_names = []

  def execute_end(self, exec_ctx):
    global enwindowbutton
    global ensecondwindow
    global windowtitle
    global entcolor
    global openedfile
    enwindowbutton = 0
    ensecondwindow = 0
    windowtitle = "window()"
    entcolor = 0
    openedfile = ""
    return RTResult().success(Number.null)
  execute_end.arg_names = []

  def execute_vkBuild(self, exec_ctx):
    # Gets intel to builder
    print("VKODE BUILDER")
    buildtake = str(exec_ctx.symbol_table.get('value'))
    print("FROM:  " + buildtake)
    buildwith = input("WITH:  ")

    # Checks if building filepack is available, from buildprefs.saver
    buildcheck = open(vkode_location + "buildprefs.saver", "r")
    buildread = buildcheck.read()

    if buildwith not in buildread:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "Error: Can't build " + buildwith + ", format unknown." + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET

    else: # Contacting the building filepack
      print("  > Initiating building filepack, build-" + buildwith + ".py")
      # Writing shit to the Cache folder because I'm retarded please forgive me
      cached = open(vkode_location + "cache/buildtake.saver", "w")
      cached.write(buildtake)
      cached.close()
      # Finally opening that filepack
      subprocess.call(vkode_location + "build-" + buildwith + ".py", shell=True)

    return RTResult().success(Number.null)
  execute_vkBuild.arg_names = ['value']

  def execute_webdownload(self, exec_ctx):
    downloadurl = str(exec_ctx.symbol_table.get('value'))
    remote_url = downloadurl
    downloadedit = downloadurl
    dotcount = 0
    for ddots in downloadedit:
      if ddots == '.':
        dotcount = dotcount + 1
    dotedit = dotcount - 1
    doteditsone = (downloadedit.replace('.', '', dotedit))
    doteditstwo = (doteditsone.replace(':', ''))
    doteditsthree = (doteditstwo.replace('/', ''))
    #print(doteditsthree)
    local_file = doteditsthree
    data = requests.get(remote_url)
    with open(local_file, 'wb')as file:
      file.write(data.content)
    return RTResult().success(Number.null)
  execute_webdownload.arg_names = ['value']

  def execute_lbr(self, exec_ctx):
    print("")
    return RTResult().success(Number.null)
  execute_lbr.arg_names = []

  def execute_location(self, exec_ctx):
    pathlocation = Path(__file__).parent.absolute()
    pathlocation = str(pathlocation)
    pathlocation = pathlocation.replace('\\', '/')
    return RTResult().success(String(pathlocation))
  execute_location.arg_names = []

  def execute_vkRunlog(self, exec_ctx):
    move_f = open(vkode_location +"devview/files/savers/position.saver")
    move = move_f.read()
    move_f.close()
    print("Current switch position: " + move)
    move_f = open(vkode_location + "log.txt", "r")
    move = move_f.read()
    print(move)
    move_f.close()
    return RTResult().success(Number.null)
  execute_vkRunlog.arg_names = []

  def execute_vkStats(self, exec_ctx):
    move_xd = "devview\\files\\stats\\stats_console.saver"
    move_f = open(vkode_location + move_xd, "r")
    print("You've opened Console " + move_f.read() + " times")
    move_f.close()
    move_f = open(vkode_location + "devview/files/stats/stats_run.saver", "r")
    print("You've used run() " + move_f.read() + " times")
    move_f.close()
    move_f = open(vkode_location + "devview/files/stats/stats_vkode.saver", "r")
    print("vkode.py was called " + move_f.read() + " times")
    move_f.close()
    move_f = open(vkode_location + "devview/files/stats/stats_builds.saver", "r")
    print("You've successfuly builded your apps " + move_f.read() + " times")
    move_f.close()
    return RTResult().success(Number.null)
  execute_vkStats.arg_names = []

  def execute_vkS(self, exec_ctx):
    move_location = vkode_location + "s.saver"
    move_f = open(move_location)
    move = move_f.read()
    move_f.close()
    print(move)
    return RTResult().success(Number.null)
  execute_vkS.arg_names = []

  def execute_locationRun(self, exec_ctx):
    global runloc

    if runloc == "":
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "You have to use run() first." + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
      return RTResult().success(Number.null)
    else:
      return RTResult().success(String(runloc))
  execute_locationRun.arg_names = []

  def execute_python(self, exec_ctx):
    move = str(exec_ctx.symbol_table.get('value'))
    move = "python " + move
    subprocess.call(move, shell=True)
    return RTResult().success(Number.null)
  execute_python.arg_names = ['value']

  def execute_varTostring(self, exec_ctx):
    move = str(exec_ctx.symbol_table.get('value'))    
    return RTResult().success(String(move))
  execute_varTostring.arg_names = ['value']

  def execute_varTointeger(self, exec_ctx):
    move = str(exec_ctx.symbol_table.get('value'))
    move_2 = int(move)    
    return RTResult().success(Number(move_2))
  execute_varTointeger.arg_names = ['value']

  global rreplace_location
  rreplace_location = 0
  global rreplace_number
  rreplace_number = 0

  def execute_varReplaceSet(self, exec_ctx):
    move = str(exec_ctx.symbol_table.get('value'))
    global rreplace_location
    global rreplace_number
    if move[0] == "-":
      rreplace_location = 0
      return RTResult().success(Number.null)
    elif move[-1] != "-":
      rreplace_location = 1
      return RTResult().success(Number.null)
    

  execute_varReplaceSet.arg_names = ['value']

  def execute_varReplace(self, exec_ctx): # 1984 -- function replacing shit needed
    move = str(exec_ctx.symbol_table.get('value'))
    move_a,move_b = move.split('-', 1)
    if move_a == '-':
      return RTResult().success(String("jupi"))

    
  execute_varReplace.arg_names = ['value']

  def execute_vkUpdate(self, exec_ctx):
    print("VKODE UPDATES")
    print("Checking for updates...")
    from vksettings import versioncheck
    verze = urlopen(versioncheck).read()
    verzedek = int(verze.decode('utf-8'))
    verzelocal_f = open(vkode_location + "version.saver", "r")
    verzelocal = int(verzelocal_f.read())
    if verzedek == verzelocal:
      print("Your VK version is up to date, everything is ok!")
    elif verzedek > verzelocal:
      print("YOUR VKODE IS NOT UPDATED!")
      ask = 1
      while ask == 1:
          print("  > PLEASE READ CAREFULLY: If you proceed, new version of 'VKode stable Windows build " + str(verzedek) + "' will be downloaded and installed. If you're using other distribution of VKode (like source files), you'll have to download it and reinstall again manually. Also, we recommend you to change the directory to somewhere safe - VKode will download the file package into the current directory. It might take a minute. Do you wish to continue?")
          yesno = input("y/n > ")
          if yesno == "y":
              print("  > Proceeding, please wait")
              subprocess.call(vkode_location + "update.py", shell=True)
              ask = 0
          elif yesno == "n":
              print("  > Cancelling process")
              ask = 0
          else:
              print("  > yes or no expected, please try again")
      ask = 0
    return RTResult().success(Number.null)
  execute_vkUpdate.arg_names = []

  def execute_editfile(self, exec_ctx):
    editfilelocation = str(exec_ctx.symbol_table.get('value'))
    fedit = open(editfilelocation, "w")
    print("  > Opened", editfilelocation, ", input the text to replace:")
    editfiletext = input()
    fedit.write(editfiletext)
    print("  > File '", editfilelocation, "' successfuly edited to", ("'"), editfiletext, "'")
    fedit.close()
    return RTResult().success(Number.null)
  execute_editfile.arg_names = ['value']


  def execute_open(self, exec_ctx):
    global openedfile
    openedfile = str(exec_ctx.symbol_table.get('value'))
    return RTResult().success(Number.null)
  execute_open.arg_names = ['value']

  def execute_fileWrite(self, exec_ctx):
    global openedfile
    move = str(exec_ctx.symbol_table.get('value'))
    if openedfile != "":
      fileopen = open(openedfile, "w")
      fileopen.write(move)
      fileopen.close()
    else:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "Cannot write the file, file location has not been set yet. Set the file location using open()" + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
    return RTResult().success(Number.null)
  execute_fileWrite.arg_names = ['value']

  def execute_fileRead(self, exec_ctx):
    global openedfile
    if openedfile != "":
      fileopen = open(openedfile, "r")
      read = fileopen.read()
      return RTResult().success(String(read))
    else:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "Cannot read the file, file location has not been set yet. Set the file location using open()" + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
  execute_fileRead.arg_names = []

  def execute_fileAppend(self, exec_ctx):
    global openedfile
    move = str(exec_ctx.symbol_table.get('value'))
    if openedfile != "":
      fileopen = open(openedfile, "a")
      fileopen.write(move)
      fileopen.close()
    else:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + "Cannot append the file, file location has not been set yet. Set the file location using open()" + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
    return RTResult().success(Number.null)
  execute_fileAppend.arg_names = ['value']
  
  def execute_web(self, exec_ctx):
    openweburl = str(exec_ctx.symbol_table.get('value'))
    webbrowser.open(openweburl, new=2)
    return RTResult().success(Number.null)
  execute_web.arg_names = ['value']

  global windowtitle
  windowtitle = "window()"
  global windowbutton
  windowbutton = "K"
  global enwindowbutton
  enwindowbutton = 0
  global ensecondwindow
  ensecondwindow = 0
  global secondbuttonvalue
  secondbuttonvalue = "Cancel"

  def execute_windowSetname(self, exec_ctx):
    global windowtitle
    windowname = str(exec_ctx.symbol_table.get('value'))
    windowtitle = windowname
    return RTResult().success(Number.null)
  execute_windowSetname.arg_names = ['value']

  def execute_windowSetbutton(self, exec_ctx):
    global windowbutton
    global enwindowbutton
    setwindowbutton = str(exec_ctx.symbol_table.get('value'))
    enwindowbutton = 1
    if setwindowbutton == "":
      enwindowbutton = 0
    if setwindowbutton == "/clear/":
      enwindowbutton = 0
    windowbutton = setwindowbutton
    return RTResult().success(Number.null)
  execute_windowSetbutton.arg_names = ['value']

  def execute_windowSetsecondbutton(self, exec_ctx):
    global ensecondwindow
    global secondbuttonvalue
    global enwindowbutton
    if enwindowbutton == 0:
      global frameinfo
      frameinfo = getframeinfo(currentframe())
      warning_set()
      global warning_sign
      print(warning_sign + 'Error: First button value has not been set. Please set the button first, windowSetbutton("")' + Style.NORMAL)
      warning_sign = Fore.RED + "  ! " + Fore.RESET
    elif enwindowbutton == 1:
      secondbuttontext = str(exec_ctx.symbol_table.get('value'))
      secondbuttonvalue = secondbuttontext
      ensecondwindow = 1
      if secondbuttontext == "":
        ensecondwindow = 0
      elif secondbuttontext == "/clear/":
        ensecondwindow = 0
    return RTResult().success(Number.null)
  execute_windowSetsecondbutton.arg_names = ['value']

  def execute_window(self, exec_ctx):
    global windowtitle
    global enwindowbutton
    global windowbutton
    global secondbuttonvalue
    windowtext = str(exec_ctx.symbol_table.get('value'))
    if enwindowbutton == 0:
      pymsgbox.alert(windowtext, windowtitle)
      return RTResult().success(Number(1))
    elif enwindowbutton == 1:
      if ensecondwindow == 0:
        pymsgbox.alert(windowtext, windowtitle, windowbutton)
        return RTResult().success(Number(1))
      elif ensecondwindow == 1:
        window_b = pymsgbox.confirm(windowtext, windowtitle, buttons=[windowbutton, secondbuttonvalue])
        if window_b == windowbutton:
          return RTResult().success(Number(1))
        elif window_b == secondbuttonvalue:
          return RTResult().success(Number(2))
  execute_window.arg_names = ['value']

  def execute_windowInput(self, exec_ctx):
    global windowtitle
    window_c = pymsgbox.prompt(windowtitle, default='This reference dates this example.')
    return RTResult().success(string(str(window_c)))
  execute_windowInput.arg_names = []
  
  def execute_vkSettings(self, exec_ctx):
    print("  > Please wait, loading vksettings.py")
    from vksettings import mezera
    from vksettings import noticeverafter
    from vksettings import nula
    from vksettings import consolerunning
    print("  > VKode SHELL BASIC SETTINGS:")
    from vksettings import vblock
    print("Vblock:", mezera, "vksettings.py vblock =", mezera, "'", vblock, "'")
    from vksettings import versioncheck
    print("Version check URL:", mezera, "vksettings.py versioncheck =", mezera, "'", versioncheck, "'")
    from vksettings import noticeversion
    print("Additional Old version notification:", mezera, "vksettings.py noticeversion =", mezera, "'", noticeversion, "'")
    from vksettings import skipstartdelay
    print("Additional Anti-crash delay:", mezera, "vksettings.py skipstartdelay =", mezera, "'", skipstartdelay, "'")
    from vksettings import deletestart
    print("Automatically deletes all lines after successful Console startup:", mezera, "vksettings.py deletestart =", mezera, "'", deletestart, "'")
    from vksettings import autodevview
    print("Auto Dev view:", mezera, "vksettings.py autodevview =", mezera, "'", autodevview, "'")
    print("vksettings.py mezera =", mezera, "'", mezera, "'")
    print("vksettings.py noticeverafter =", mezera, "'", noticeverafter, "'")
    print("vksettings.py nula =", mezera, "'", nula, "'")
    print("vksettings.py consolerunning (Default settings) =", mezera, "'", consolerunning, "'")
    print("TO EDIT THESE VALUES, OPEN VKSETTINGS.TXT. Changes in vksettings.py will not work")
    return RTResult().success(Number.null)
  execute_vkSettings.arg_names = []

  def execute_vkDevview(self, exec_ctx):
    os.startfile("devview.exe")
    return RTResult().success(Number.null)
  execute_vkDevview.arg_names = []

  def execute_input(self, exec_ctx):
    text = input()
    move = str(text)
    return RTResult().success(String(move))
  execute_input.arg_names = []

  def execute_input_int(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer. Try again!")
    return RTResult().success(Number(number))
  execute_input_int.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls') 
    return RTResult().success(Number.null)
  execute_clear.arg_names = []

  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]

  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RTResult().success(Number.null)
  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null)
  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list",
        exec_ctx
      ))

    return RTResult().success(Number(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")
    
    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be string",
        exec_ctx
      ))

    fn = fn.value

    logtext = fn
    position = open(vkode_location + "devview/files/savers/position.saver", "r")
    logposition = position.read()
    position.close()

    if ":" not in logtext:
      pathlocation = __file__
      pathlocation = pathlocation[:-8]
      logtext = pathlocation + logtext
      logtext = logtext.replace("\\", "/")

    global runloc
    runloc = logtext
    runloc = runloc.replace("\\", "/")
    #print(debugl + runloc)

    with open(vkode_location + "log.txt", "a") as logt:
      logt.write("\n")
      cas = datetime.now()
      casp = str(cas)
      logwrite = (logtext + " - " + casp)
      logt.write(logwrite)
      logt.close()
    
    if logposition == "1":
      devview1 = open(vkode_location + "devview/files/savers/1.saver", "w")
      devview1.write(logtext)
      devview1.close()
    elif logposition == "2":
      devview2 = open(vkode_location + "devview/files/savers/2.saver", "w")
      devview2.write(logtext)
      devview2.close()
    elif logposition == "3":
      devview3 = open(vkode_location + "devview/files/savers/3.saver", "w")
      devview3.write(logtext)
      devview3.close()

    wposition = open(vkode_location + "devview/files/savers/position.saver", "w")
    if logposition == "1":
      wposition.write("2")
    elif logposition == "2":
      wposition.write("3")
    elif logposition == "3":
      wposition.write("1")
    wposition.close()

    move_f = open(vkode_location + "devview/files/stats/stats_run.saver", "r")
    move = move_f.read()
    move_int = int(move)
    move_f.close()
    move_int = move_int + 1
    move = str(move_int)
    move_f = open(vkode_location + "devview/files/stats/stats_run.saver", "w")
    move_f.write(move)
    move_f.close()

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)
    
    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))
    return RTResult().success(Number.null)
  execute_run.arg_names = ["fn"]

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len					= BuiltInFunction("len")
BuiltInFunction.run					= BuiltInFunction("run")
BuiltInFunction.kill        = BuiltInFunction("kill")
BuiltInFunction.readfile    = BuiltInFunction("readfile")
BuiltInFunction.editfile    = BuiltInFunction("editfile")
BuiltInFunction.web         = BuiltInFunction("web")
BuiltInFunction.window      = BuiltInFunction("window")
BuiltInFunction.windowSetname     = BuiltInFunction("windowSetname")
BuiltInFunction.windowSetbutton     = BuiltInFunction("windowSetbutton")
BuiltInFunction.windowSetsecondbutton     = BuiltInFunction("windowSetsecondbutton")
BuiltInFunction.vkUpdate    = BuiltInFunction("vkUpdate")
# BuiltInFunction.openfile  = BuiltInFunction("openfile")
BuiltInFunction.webdownload = BuiltInFunction("webdownload")
BuiltInFunction.lbr         = BuiltInFunction("lbr")
BuiltInFunction.location    = BuiltInFunction("location")
BuiltInFunction.file        = BuiltInFunction("file")
BuiltInFunction.time        = BuiltInFunction("time")
BuiltInFunction.vkSettings  = BuiltInFunction("vkSettings")
BuiltInFunction.vkDevview   = BuiltInFunction("vkDevview")
BuiltInFunction.tacet       = BuiltInFunction("tacet")
BuiltInFunction.printstyle  = BuiltInFunction("printstyle")
BuiltInFunction.printstyleSetcolor  = BuiltInFunction("printstyleSetcolor")
BuiltInFunction.style       = BuiltInFunction("style")
BuiltInFunction.devview     = BuiltInFunction("devview")
BuiltInFunction.end         = BuiltInFunction("end")
BuiltInFunction.vkBuild       = BuiltInFunction("vkBuild")
BuiltInFunction.use         = BuiltInFunction("use")
BuiltInFunction.open        = BuiltInFunction("open")
BuiltInFunction.fileWrite   = BuiltInFunction("fileWrite")
BuiltInFunction.fileRead    = BuiltInFunction("fileRead")
#BuiltInFunction.network    = BuiltInFunction("network")
BuiltInFunction.vkRunlog    = BuiltInFunction("vkRunlog")
BuiltInFunction.vkS         = BuiltInFunction("vkS")
BuiltInFunction.python      = BuiltInFunction("python")
BuiltInFunction.locationRun = BuiltInFunction("locationRun")
BuiltInFunction.varTostring = BuiltInFunction("varTostring")
BuiltInFunction.varTointeger = BuiltInFunction("varTointeger")
BuiltInFunction.vkStats     = BuiltInFunction("vkStats")
BuiltInFunction.varReplace  = BuiltInFunction("varReplace")
BuiltInFunction.fileAppend  = BuiltInFunction("fileAppend")
BuiltInFunction.windowInput = BuiltInFunction("windowInput")

# context

class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None


# symbol table
class SymbolTable:
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent

  def get(self, name):
    value = self.symbols.get(name, None)
    if value == None and self.parent:
      return self.parent.get(name)
    return value

  def set(self, name, value):
    self.symbols[name] = value

  def remove(self, name):
    del self.symbols[name]


# interpreter

class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'AND'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(TT_KEYWORD, 'OR'):
      result, error = left.ored_by(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'NOT'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RTResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Number.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Number.null if should_return_null else expr_value)

    return res.success(Number.null)

  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Number(1)

    i = start_value.value

    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value
    
    while condition():
      context.symbol_table.set(node.var_name_tok.value, Number(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
      
      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
    
    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_ReturnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Number.null
    
    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RTResult().success_break()


# run

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("IS_num", BuiltInFunction.is_number)
global_symbol_table.set("IS_str", BuiltInFunction.is_string)
global_symbol_table.set("IS_list", BuiltInFunction.is_list)
global_symbol_table.set("IS_fun", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("kill", BuiltInFunction.kill)
global_symbol_table.set("readfile", BuiltInFunction.readfile)
global_symbol_table.set("editfile", BuiltInFunction.editfile)
global_symbol_table.set("web", BuiltInFunction.web)
global_symbol_table.set("window", BuiltInFunction.window)
global_symbol_table.set("windowSetname", BuiltInFunction.windowSetname)
global_symbol_table.set("windowSetbutton", BuiltInFunction.windowSetbutton)
global_symbol_table.set("windowSetsecondbutton", BuiltInFunction.windowSetsecondbutton)
global_symbol_table.set("vkUpdate", BuiltInFunction.vkUpdate)
# global_symbol_table.set("openfile", BuiltInFunction.openfile)
global_symbol_table.set("webdownload", BuiltInFunction.webdownload)
global_symbol_table.set("lbr", BuiltInFunction.lbr)
global_symbol_table.set("location", BuiltInFunction.location)
global_symbol_table.set("file", BuiltInFunction.file)
global_symbol_table.set("time", BuiltInFunction.time)
global_symbol_table.set("vkSettings", BuiltInFunction.vkSettings)
global_symbol_table.set("vkDevview", BuiltInFunction.vkDevview)
global_symbol_table.set("tacet", BuiltInFunction.tacet)
global_symbol_table.set("printstyle", BuiltInFunction.printstyle)
global_symbol_table.set("printstyleSetcolor", BuiltInFunction.printstyleSetcolor)
global_symbol_table.set("style", BuiltInFunction.style)
global_symbol_table.set("devview", BuiltInFunction.devview)
global_symbol_table.set("end", BuiltInFunction.end)
global_symbol_table.set("vkBuild", BuiltInFunction.vkBuild)
global_symbol_table.set("use", BuiltInFunction.use)
global_symbol_table.set("open", BuiltInFunction.open)
global_symbol_table.set("fileWrite", BuiltInFunction.fileWrite)
global_symbol_table.set("fileRead", BuiltInFunction.fileRead)
global_symbol_table.set("vkRunlog", BuiltInFunction.vkRunlog)
global_symbol_table.set("vkS", BuiltInFunction.vkS)
global_symbol_table.set("python", BuiltInFunction.python)
global_symbol_table.set("locationRun", BuiltInFunction.locationRun)
global_symbol_table.set("varTostring", BuiltInFunction.varTostring)
global_symbol_table.set("varTointeger", BuiltInFunction.varTointeger)
global_symbol_table.set("vkStats", BuiltInFunction.vkStats)
global_symbol_table.set("varReplace", BuiltInFunction.varReplace)
global_symbol_table.set("fileAppend", BuiltInFunction.fileAppend)
global_symbol_table.set("windowInput", BuiltInFunction.windowInput)


def run(fn, text):
  # generates tokens
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error
  
  # generates ast
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error

  # LINE 2850 INCIDENT
  # Approx. 472 minutes wasted, read at http://docs.vkode.xyz/incidents/2850.html



# 1986 -- Libs dependencies
# INSTALLED LIBRARIES FOLLOW
# These are libraries installed by Dev View.

