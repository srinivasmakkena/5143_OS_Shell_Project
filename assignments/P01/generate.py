
import random,re
def gen_longest_expression():
  def random_longest_math_expression(lowest_number =1, highest_number = 10, min_length = 1, max_length = 5):
    operators = [ '*', '/', '+', '-']
    operands = [random.randint(lowest_number, highest_number) for _ in range(random.randint(min_length, max_length))]
    expression = ""
    for i in range(len(operands) - 1):
      operator = random.choice(operators)
      operator2 = random.choice(operators)
      expression += f"{operands[i]}{operator}"  
      operator = random.choice(operators)
      if not expression.strip()[-1].isdigit():
        expression += str(operands[-1])
      flag = random.choice([True, False])
      parenthesis_count = expression.count('(')
      parenthesis_count -= expression.count(')')
      for _ in range(parenthesis_count):
        expression += ')'
        expression += str(operator)
    if len(expression) and not expression.strip()[-1].isdigit():
      expression += str(operands[-1])
    parenthesis_count = expression.count('(')
    parenthesis_count -= expression.count(')')
    for _ in range(parenthesis_count):
      expression += ')'
    return expression
  longest_expression = random_longest_math_expression()
  operator = random.choice([ '*', '/', '+', '-'])
  result = re.sub(r'(\d+) \s*\(', r'\1 '+operator+' (', longest_expression)
  longest_expression = re.sub(r'\) \s*\(', ') '+operator+' (', result)
  # print(longest_expression)

  while '^' in longest_expression:
    longest_expression = longest_expression.replace('^', '**')
  # print(longest_expression)
  try:
    if longest_expression.isdigit():
      answer = int(longest_expression)
    else:
      answer = eval(longest_expression)
  except Exception as ex:
    answer = "Error:" + str(ex)
    answer = 1
  return (longest_expression,answer)

def string_to_decimal_list(text):
  if len([ord(char) - 40 for char in text])%2==0:
    text += "1"
  return [ord(char) - 40 for char in text]

def decimal_list_to_string(decimal_list):
  return ''.join(chr(decimal+40) for decimal in decimal_list)

# import os 
# os.system("clear")
# text = longest_expression
# result = string_to_decimal_list(text)
# print("\nDecimal List - "+ str(result))
# text = decimal_list_to_string(result)
# print("\nEquation: " + text)
# print("\nAnswer: "+ str(answer))
# print("\n\n\n\n\n")
