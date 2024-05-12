# Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
# — Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
# — Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
# — Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
# • Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
# • Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
# • Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.
#
# Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
# Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
from random import randint

DATABASE_URL = "sqlite:///mydatabase.db"  # создаем базу данных в корневой директории
database = databases.Database(DATABASE_URL)  # переменная из класса Database
metadata = sqlalchemy.MetaData()  # метаданные

app = FastAPI()

customers = sqlalchemy.Table(
    "customers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(25)),
    sqlalchemy.Column("surname", sqlalchemy.String(25)),
    sqlalchemy.Column("email", sqlalchemy.String(40)),
    sqlalchemy.Column("password", sqlalchemy.String(15)),
)

items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(20)),
    sqlalchemy.Column("description", sqlalchemy.String(100)),
    sqlalchemy.Column("price", sqlalchemy.Integer),
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("customer_id", sqlalchemy.ForeignKey(customers.c.id)),
    sqlalchemy.Column("item_id", sqlalchemy.ForeignKey(items.c.id)),
    sqlalchemy.Column("date", sqlalchemy.DateTime()),
    sqlalchemy.Column("status", sqlalchemy.Boolean())
)


@app.get('/')
async def get_main():
    return {'Hello': 'World!'}


class CustomerIn(BaseModel):
    name: str = Field(..., max_length=25)
    surname: str = Field(..., max_length=25)
    email: EmailStr = Field(..., max_length=40)
    password: str = Field(..., min_length=6, max_length=15)


class Customer(CustomerIn):
    id: int


class ItemIn(BaseModel):
    name: str = Field(..., max_length=20)
    description: str = Field(..., max_length=100)
    price: int = Field(...)


class Item(ItemIn):
    id: int


class OrderIn(BaseModel):
    customer_id: int = Field(...)
    item_id: int = Field(...)
    date: datetime = Field(...)
    status: bool = Field(...)


class Order(OrderIn):
    id: int


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


@app.get("/create_table/{cnt}")
async def create_table(cnt: int):
    for i in range(cnt):
        query = customers.insert().values(name=f'customer{i}',
                                          surname=f'surname{i}',
                                          email=f'customer{i}@mail.ru',
                                          password=f'password{i}')
        await database.execute(query)
    return {"msg": "database_ready"}


@app.get("/create_items/{cnt}")
async def create_items(cnt: int):
    for i in range(cnt):
        query = items.insert().values(name=f'item{i}',
                                      description=f'description{i}',
                                      price=randint(1, 10))
        await database.execute(query)
    return {"msg": "database_ready"}


@app.get('/customers/', response_model=List[Customer])
async def get_customers():
    query = customers.select()
    return await database.fetch_all(query)


@app.get('/customers/{customer_id}', response_model=Customer)
async def get_customer(customer_id: int):
    query = customers.select().where(customers.c.id == customer_id)
    return await database.fetch_one(query)


@app.post('/customers/', response_model=CustomerIn)
async def add_customer(customer: CustomerIn):
    query = customers.insert().values(**customer.model_dump())
    create_id = await database.execute(query)
    return await get_customer(create_id)


@app.put('/customers/{customer_id}', response_model=Customer)
async def update_customer(customer_id: int, customer: CustomerIn):
    query = customers.update().where(customers.c.id == customer_id).values(**customer.model_dump())
    await database.execute(query)
    return await get_customer(customer_id)


@app.delete('/customers/')
async def delete_customer(customer_id: int):
    query = customers.delete().where(customers.c.id == customer_id)
    await database.execute(query)


@app.get('/items/', response_model=List[Item])
async def get_item():
    query = items.select()
    return await database.fetch_all(query)


@app.get('/items/{item_id}', response_model=Item)
async def get_item(item_id: int):
    query = items.select().where(items.c.id == item_id)
    return await database.fetch_one(query)


@app.post('/items/', response_model=ItemIn)
async def add_item(item: ItemIn):
    query = items.insert().values(**items.model_dump())
    create_id = await database.execute(query)
    return await get_item(create_id)


@app.put('/items/{item_id}', response_model=Item)
async def update_item(item_id: int, item: ItemIn):
    query = items.update().where(items.c.id == item_id).values(**item.model_dump())
    await database.execute(query)
    return await get_item(item_id)


@app.delete('/items/')
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)


@app.get('/orders/', response_model=List[Order])
async def get_order():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/orders/{order_id}', response_model=Order)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.post('/orders/', response_model=OrderIn)
async def add_order(order: OrderIn):
    query = orders.insert().values(**order.model_dump())
    create_id = await database.execute(query)
    return await get_order(create_id)


@app.put('/orders/{order_id}', response_model=Order)
async def update_order(order_id: int, order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(**order.model_dump())
    await database.execute(query)
    return await get_order(order_id)


@app.delete('/orders/')
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
