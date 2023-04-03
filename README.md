# Pyome

# Project Title

A brief description of the project, its purpose, and main features.

## Table of Contents

- [Project Title](#project-title)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Installation

Detailed instructions on how to install the project, including prerequisites and any required dependencies.

## Usage

The Engine can be imported as a module or executed from the shell. To run the Engine, just run 
inside the project root directory:

```commandline
$ python3 src/engine.py

PyOME: Python Order Matching Engine
Author: Henrique de Carvalho

>>> 
```

The grammar of the program is:
```Python
>>> limit <buy|sell> <price> <quantity>
>>> market <buy|sell> <quantity>
>>> change order <id> <price> <quantity>
>>> delete order <id> # ignore
>>> print book
>>> help

Where:
    <price> is a real number.
    <quantity> is an integer.
    <id> is an integer.
```

## Examples

Provide examples of how to use the project in various scenarios. Include code snippets and, if applicable, screenshots or GIFs to demonstrate the project in action.

## 
```
>>> print book 
        Buy Orders     |     Sell Orders     
  -------------------------------------------
                       |    100 @ 10.00 (1)

>>> limit sell 11 100
Order created: sell 100 @ 11.00 (2)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
                       |    100 @ 10.00 (1)
                       |    100 @ 11.00 (2)

>>> limit sell 1 1  
Order created: sell 1 @ 1.00 (3)
>>> limit sell 10000 10000
Order created: sell 10000 @ 10000.00 (4)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
                       |      1 @ 1.00 (3)
                       |    100 @ 10.00 (1)
                       |    100 @ 11.00 (2)
                       |  10000 @ 10000.00 (4)

>>> market buy 10000
Trade, price: 1.00, qty: 1.0
Trade, price: 100.00, qty: 10.0
Trade, price: 100.00, qty: 11.0
Trade, price: 9799.00, qty: 10000.0
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
                       |    201 @ 10000.00 (4)

>>> market buy 300
Trade, price: 201.00, qty: 10000.0
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------

>>> limit buy 9.99 100
Order created: buy 100 @ 9.99 (7)
>>> limit buy 9.98 200
Order created: buy 200 @ 9.98 (8)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      100 @ 9.99 (7)   |                     
      200 @ 9.98 (8)   |                     

>>> limit buy 10.01 300
Order created: buy 300 @ 10.01 (9)
>>> limit sell 10.05 300
Order created: sell 300 @ 10.05 (10)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      300 @ 10.01 (9)  |    300 @ 10.05 (10)
      100 @ 9.99 (7)   |                     
      200 @ 9.98 (8)   |                     

>>> limit sell 10.07 100
Order created: sell 100 @ 10.07 (11)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      300 @ 10.01 (9)  |    300 @ 10.05 (10)
      100 @ 9.99 (7)   |    100 @ 10.07 (11)
      200 @ 9.98 (8)   |                     

>>> market buy 100
Trade, price: 100.00, qty: 10.05
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      300 @ 10.01 (9)  |    200 @ 10.05 (10)
      100 @ 9.99 (7)   |    100 @ 10.07 (11)
      200 @ 9.98 (8)   |                     

>>> change order 9 10.06 300
Trade, price: 200.00, qty: 10.05
Order changed. New order: buy 100 @ 10.06 (9)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      100 @ 10.06 (9)  |    100 @ 10.07 (11)
      100 @ 9.99 (7)   |                     
      200 @ 9.98 (8)   |                     

>>> market sell 100
Trade, price: 100.00, qty: 10.06
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      100 @ 9.99 (7)   |    100 @ 10.07 (11)
      200 @ 9.98 (8)   |                     

>>> cancel order 7
Order cancelled.
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      200 @ 9.98 (8)   |    100 @ 10.07 (11)

>>> limit buy 100 10.05
Error: Parsing error.
>>> limit buy 10.5 100
Trade, price: 100.00, qty: 10.07
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      200 @ 9.98 (8)   |                     

>>> 

```


## Configuration

Describe any available configuration options, including configuration file format and location, environment variables, and command-line options.

## Contributing

Information about contributing to the project, such as coding standards, branching strategy, and how to submit pull requests.

## License

Include information about the project's license (e.g., MIT, GPL, etc.) and a link to the full license text.
