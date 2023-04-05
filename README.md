# PyOME

PyOME is a simple Python order matching engine designed for simplicity and efficiency.

## Installation

This project depends only on the Python Standard Library. No additional dependencies are required.
Just clone the repository and you are ready to go.

## Usage

The Engine can be imported as a module or executed from the shell. To run the Engine, navigate 
to the project root directory and execute the command: 

```commandline
$ python3 src/engine.py
PyOME v0.1 - A Python Order Matching Engine
Author: Henrique de Carvalho
Type "help" to print commands.
>>> 
```

Type `help` to display a list of commands:
```Python
>>> help

Commands:
      limit <buy|sell:str> <price:float> <quantity:int>     places a limit order
      market <buy|sell:str> <quantity:int>                  places a market order
      cancel order <id:int>                                 cancels an order
      change order <id:int> <price:float> <quantity:int>    changes an order
      print book                                            prints the book of orders
      help                                                  displays this message
      exit                                                  exits engine
```

Users must adhere to the specified syntax and data types (`str`, `float`, `int`), otherwise a 
parsing error will occur. Informative messages are displayed after each command. The program is designed to prevent errors, so feel free to experiment and test its functionality.

Order descriptions follow the syntax:
```commandline
<quantity:int> @ <price:float> (<id:int>)
```
For example, the order `200 @ 9.98 (16)` has `quantity` of 200, `price` of 9.98 and 
`id` of 16. This sintax is showed after an order is placed or when the book is printed.


## Examples

Here are some examples demonstrating how to use the program.

#### Placing limit orders and printing the book. 
Note that it is not necessary to specify all the decimal places, the program will fill in 
any missing 0s.

```commandline
>>> limit buy 10.1 100
Order created: buy 100 @ 10.10 (1)
>>> limit buy 10.15 100
Order created: buy 100 @ 10.15 (2)
>>> limit buy 10 300
Order created: buy 300 @ 10.00 (3)
>>> limit sell 10.20 200
Order created: sell 200 @ 10.20 (4)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      100 @ 10.15 (2)  |    200 @ 10.20 (4)
      100 @ 10.10 (1)  |                     
      300 @ 10.00 (3)  |                     
```
#### Placing market orders

The market orders will be executed until they are fulfilled. Descriptive trade messages are 
displayed whenever orders are matched.

```commandline
>>> market sell 250
Trade, price: 10.15, qty: 100
Trade, price: 10.10, qty: 100
Trade, price: 10.00, qty: 50
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      250 @ 10.00 (3)  |    200 @ 10.20 (4)
      
>>> market buy 100
Trade, price: 10.20, qty: 100
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      250 @ 10.00 (3)  |    100 @ 10.20 (4)
```

#### Modifying orders

When orders are modified, a descriptive message displaying the new order will appear. As shown below, when a modified order has favorable opposing orders (e.g., a sell order is placed with a price equal to or higher than the buy order), the order will be executed at the price already in the book. This behavior aligns with the expectations of the buyer.

```commandline
>>> change order 3 10.19 250
Order changed. New order: buy 250 @ 10.19 (3)
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
      250 @ 10.19 (3)  |    100 @ 10.20 (4)

>>> change order 4 10.18 200
Trade, price: 10.19, qty: 200
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------
       50 @ 10.19 (3)  |                     
```
#### Cancelling Orders

Naturally, executed orders cannot be cancelled. Active orders, however, can be cancelled at any 
time.

```commandline
>>> cancel order 4
Error: This order was executed or cancelled.
>>> cancel order 3
Order cancelled.
>>> print book

        Buy Orders     |     Sell Orders     
  -------------------------------------------

```
#### Exiting the program

```commandline
>>> exit
Exiting PyOME.
```

## Implementation Details

The order matching engine has three main components: the engine, the book and the order. 
Each of these components are implemented in separate a source file inside the `src` directory: 

```commandline
└── src 
 ├── book.py
 ├── engine.py
 └── order.py
```

In `order.py` the class `Order` is implemented to represent a buy or sell order of a stock. In 
`book.py` the class `Book` is implemented to manage the order book for a stock. In `engine.py` 
the class `MatchingEngine` is implemented to receive and execute user commands and control the 
book class. The actual matching logic takes place in the `Book`, while the `MatchingEngine` is 
responsible 
for controlling the book with respect to adding, changing and cancelling orders.

The implementation of these operations (match, add, change, and cancel) attempt to achieve 
optimal performance. Heaps are used to implement minimum and maximum priority queues, for 
selling and buying queues, respectively. 

Matching an added order with an opposing order occurs right before adding, in the same functions 
`add_{limit|market}_order`.
The actual matching has linearithmic worst-case time complexity, although this would require an 
order to clear the entire book. It is more likely that an order will be matched in constant time.

Adding orders to the heaps take logarithmic time complexity. Changing an order has the same time 
complexity. Deleting an order, on the other hand, has constant time complexity. Since for adding 
and 
changing orders,
involve a matching operation, they are bound by linearithmic worst-case time complexity. However,
as 
explained, these are more likely to be bound to logarithmic time complexity in practice.

The code is 
extensively 
commented and in-depth 
implementation 
details
can be found in function and 
class docstrings, under <i>Notes</i> section.