use std::str::Chars;

#[derive(Debug, PartialEq)]
enum Token {
    Number(f64),
    Plus,
    Minus,
    Star,
    Slash,
    Power,
    LParen,
    RParen,
    Invalid,
    End,
}

#[derive(Debug)]
enum ParseError {
    DivisionByZero,
    TrailingTokens,
    EmptyExpression,
    InvalidSyntax,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::DivisionByZero => write!(f, "division by zero"),
            Self::TrailingTokens => write!(f, "trailing unparsed tokens"),
            Self::EmptyExpression => write!(f, "empty expression"),
            Self::InvalidSyntax => write!(f, "invalid syntax"),
        }
    }
}

struct Lexer<'a> {
    chars: Chars<'a>,
    current: Option<char>,
}

impl<'a> Lexer<'a> {
    fn new(input: &'a str) -> Self {
        let mut lexer = Self {
            chars: input.chars(),
            current: None,
        };
        lexer.advance();
        lexer
    }

    fn advance(&mut self) {
        self.current = self.chars.next();
    }

    fn next_token(&mut self) -> Token {
        while let Some(c) = self.current {
            match c {
                ' ' | '\t' | '\n' | '\r' => {
                    self.advance();
                }
                '0'..='9' | '.' => {
                    let mut num_str = String::new();
                    while let Some(ch) = self.current {
                        if ch.is_ascii_digit() || ch == '.' {
                            num_str.push(ch);
                            self.advance();
                        } else {
                            break;
                        }
                    }
                    return match num_str.parse::<f64>() {
                        Ok(num) => Token::Number(num),
                        Err(_) => Token::Invalid,
                    };
                }
                '+' => {
                    self.advance();
                    return Token::Plus;
                }
                '-' => {
                    self.advance();
                    return Token::Minus;
                }
                '*' => {
                    self.advance();
                    if self.current == Some('*') {
                        self.advance();
                        return Token::Power;
                    }
                    return Token::Star;
                }
                '/' => {
                    self.advance();
                    return Token::Slash;
                }
                '^' => {
                    self.advance();
                    return Token::Power;
                }
                '(' => {
                    self.advance();
                    return Token::LParen;
                }
                ')' => {
                    self.advance();
                    return Token::RParen;
                }
                _ => {
                    self.advance();
                    return Token::Invalid;
                }
            }
        }
        Token::End
    }
}

struct Parser<'a> {
    lexer: Lexer<'a>,
    current_token: Token,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self {
        let mut lexer = Lexer::new(input);
        let current_token = lexer.next_token();
        Self {
            lexer,
            current_token,
        }
    }

    fn advance(&mut self) {
        self.current_token = self.lexer.next_token();
    }

    fn parse(&mut self) -> Result<f64, ParseError> {
        if self.current_token == Token::End {
            return Err(ParseError::EmptyExpression);
        }
        let result = self.expression()?;
        if self.current_token != Token::End {
            return Err(ParseError::TrailingTokens);
        }
        Ok(result)
    }

    fn expression(&mut self) -> Result<f64, ParseError> {
        let mut result = self.term()?;
        while matches!(self.current_token, Token::Plus | Token::Minus) {
            let is_plus = self.current_token == Token::Plus;
            self.advance();
            let rhs = self.term()?;
            if is_plus {
                result += rhs;
            } else {
                result -= rhs;
            }
        }
        Ok(result)
    }

    fn term(&mut self) -> Result<f64, ParseError> {
        let mut result = self.unary()?;
        while matches!(self.current_token, Token::Star | Token::Slash) {
            let is_mul = self.current_token == Token::Star;
            self.advance();
            let rhs = self.unary()?;
            if is_mul {
                result *= rhs;
            } else {
                if rhs == 0.0 {
                    return Err(ParseError::DivisionByZero);
                }
                result /= rhs;
            }
        }
        Ok(result)
    }

    fn unary(&mut self) -> Result<f64, ParseError> {
        if self.current_token == Token::Plus {
            self.advance();
            return self.unary();
        }
        if self.current_token == Token::Minus {
            self.advance();
            return Ok(-self.unary()?);
        }
        self.power()
    }

    fn power(&mut self) -> Result<f64, ParseError> {
        let base = self.primary()?;
        if self.current_token == Token::Power {
            self.advance();
            let exponent = self.unary()?;
            return Ok(base.powf(exponent));
        }
        Ok(base)
    }

    fn primary(&mut self) -> Result<f64, ParseError> {
        match self.current_token {
            Token::Number(num) => {
                self.advance();
                Ok(num)
            }
            Token::LParen => {
                self.advance();
                let result = self.expression()?;
                if self.current_token != Token::RParen {
                    return Err(ParseError::InvalidSyntax);
                }
                self.advance();
                Ok(result)
            }
            _ => Err(ParseError::InvalidSyntax),
        }
    }
}

/// Safely evaluates a mathematical string expression.
/// Supported operators: +, -, *, /, ^ and ** (power)
pub fn evaluate_expression(expr: &str) -> Result<f64, String> {
    let mut parser = Parser::new(expr);
    parser.parse().map_err(|e| e.to_string())
}
