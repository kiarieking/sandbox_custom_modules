
# Endpoints - ERP

Endpoints that can be used to integrate with the Quatrix ODOO ERP.


## API Reference

### 1. Partners Endpoints
## 
#### Get All Partners

```http
  GET /api/partners
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Get Single Partner

```http
  GET /api/partners/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key` | `string` | **Required**. Your API key        |
| `id`      | `string` | **Required**. carrier id          |


#### Create Partner

```http
  POST /api/partners
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `partner`            | `string`   | **Required**. carrier name        |
| `phone`              | `string`   | **Required**. carrier phone       |
| `email`              | `string`   | **Required**. carrier email       |
| `carrier_id`         | `string`   | **Required**. carrier id (core)   |
| `shipper_id`         | `string`   | **Required**. shipper id (core)   |
| `is_vendor`          | `boolean`  | **Required**. is_vendor?          |
| `is_shipper`         | `boolean`  | **Required**. is_shipper?         |
| `is_partner_vatable` | `boolean`  | **Required**. is_vendor?          |

#### Edit Partner

```http
  PATCH /api/partners/${carrier_id}
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `partner`            | `string`   | **Required**. carrier name        |
| `phone`              | `string`   | **Required**. carrier phone       |
| `email`              | `string`   | **Required**. carrier email       |
| `carrier_id`         | `string`   | **Required**. carrier id (core)   |
| `shipper_id`         | `string`   | **Required**. shipper id (core)   |
| `is_vendor`          | `boolean`  | **Required**. is_vendor?          |
| `is_shipper`         | `boolean`  | **Required**. is_shipper?         |
| `is_partner_vatable` | `boolean`  | **Required**. is_vendor?          |


### 2. Shippers Endpoints
## 
#### Get All Shippers

```http
  GET /api/shippers
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Get Single Shipper

```http
  GET /api/shippers/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key` | `string` | **Required**. Your API key        |
| `id`      | `string` | **Required**. carrier id          |


#### Create Shipper

```http
  POST /api/shippers
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `partner`            | `string`   | **Required**. carrier name        |
| `phone`              | `string`   | **Required**. carrier phone       |
| `email`              | `string`   | **Required**. carrier email       |
| `carrier_id`         | `string`   | **Required**. carrier id (core)   |
| `shipper_id`         | `string`   | **Required**. shipper id (core)   |
| `is_vendor`          | `boolean`  | **Required**. is_vendor?          |
| `is_shipper`         | `boolean`  | **Required**. is_shipper?         |
| `is_partner_vatable` | `boolean`  | **Required**. is_vendor?          |

#### Edit Shipper

```http
  PATCH /api/shippers/${shipper_id}
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `partner`            | `string`   | **Required**. carrier name        |
| `phone`              | `string`   | **Required**. carrier phone       |
| `email`              | `string`   | **Required**. carrier email       |
| `carrier_id`         | `string`   | **Required**. carrier id (core)   |
| `shipper_id`         | `string`   | **Required**. shipper id (core)   |
| `is_vendor`          | `boolean`  | **Required**. is_vendor?          |
| `is_shipper`         | `boolean`  | **Required**. is_shipper?         |
| `is_partner_vatable` | `boolean`  | **Required**. is_vendor?          |


## 3. Products Endpoints
## 

#### Get All Products

```http
  GET /api/products
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |



#### Get Products Using Shipper ID

```http
  GET /api/${shipper_id}/products
```

| Parameter    | Type     | Description                       |
| :----------- | :------- | :-------------------------------- |
| `api_key`    | `string` | **Required**. Your API key        |
| `shipper_id` | `integer` | **Required**. Shipper id         |


#### Get Single Product

```http
  GET /api/products/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key` | `string` | **Required**. Your API key        |
| `id`      | `string` | **Required**. product id          |


#### Create Product

```http
  POST /api/products
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `name`               | `string`   | **Required**. product name        |
| `price`              | `string`   | **Required**. product price       |
| `shupper_id`         | `string`   | **Required**. shipper ID (core)   |
| `default_code`       | `string`   | **Required**. Internal Reference  |
| `core_product_id`    | `string`   | **Required**. product ID (core)   |


#### Edit/Update Product

```http
  PATCH /api/products/${id}
```

| Parameter            | Type       | Description                       |
| :------------------- | :--------- | :-------------------------------- |
| `api_key`            | `string`   | **Required**. Your API key        |
| `name`               | `string`   | **Required**. product name        |
| `price`              | `string`   | **Required**. product price       |
| `shupper_id`         | `string`   | **Required**. shipper ID (core)   |
| `default_code`       | `string`   | **Required**. Internal Reference  |
| `core_product_id`    | `string`   | **Required**. product ID (core)   |



## 4. Dispatch Endpoints
## 

#### Get All Dispatch Records

```http
  GET /api/dispatch
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |


#### Get Single Dispatch Record

```http
  GET /api/dispatch/${id}
```

| Parameter | Type      | Description                |
| :-------- | :-------- | :------------------------- |
| `api_key` | `string`  | **Required**. Your API key |
| `id`      | `integer` | **Required**. Dispatch id  |



#### Get Single Dispatch Record By Order Number

```http
  GET /api/dispatch/order/${order_no}
```

| Parameter | Type      | Description                |
| :-------- | :-------- | :------------------------- |
| `api_key` | `string`  | **Required**. Your API key |
| `order_no`| `integer` | **Required**. Order Number |


#### Create Dispatch Record

```http
  POST /api/dispatch
```

| Parameter       | Type               | Description                   |
| :-------------- | :----------------- | :-----------------------------|
| `api_key`       | `string`           | **Required**. Your API key    |
| `shipper_id`    | `string`           | **Required**. Core shipper ID |
| `vehicle_id`    | `string`           | **Required**. Core Vehicle ID |
| `date_dispatch` | `string`           | **Required**. Date Dispatch   |
| `date_delivery` | `string`           | **Required**. Date Delivery   |
| `order_line`    | `array of objects` | **Required**. Order lines     |

#### order_line object parameters

| Parameter         | Type               | Description                   |
| :---------------- | :----------------- | :-----------------------------|
| `core_product_id` | `string`           | **Required**. Core Product ID |
| `order_no`        | `string`           | **Required**. Order Number    |
| `quantity`        | `float`            | **Required**. Quantity        |
| `description`     | `string`           | **Required**. Description     |




## 5. Vehicle Models Endpoints
## 

#### Get Vehicle Models

```http
  GET /api/vehicles/models
```

| Parameter | Type      | Description                |
| :-------- | :-------- | :------------------------- |
| `api_key` | `string`  | **Required**. Your API key |


#### Add Vehicle Models

```http
  GET /api/vehicles/models
```

| Parameter        | Type      | Description                |
| :--------------- | :-------- | :------------------------- |
| `api_key`        | `string`  | **Required**. Your API key |
| `model`          | `string`  | **Required**. Model        |
| `manufacturer`   | `string`  | **Required**. Manufacturer |



## 6. Vehicles Endpoints
## 

#### Create Vehicle Record

```http
  POST /api/vehicles
```

| Parameter       | Type               | Description                   |
| :-------------- | :----------------- | :-----------------------------|
| `api_key`       | `string`           | **Required**. Your API key    |
| `model`         | `string`           | **Required**. Vehicle Model   |
| `carrier_id`    | `string`           | **Required**. Core Carrier ID |
| `vehicle_id`    | `string`           | **Required**. Core Vehicle ID |
| `license_plate` | `string`           | **Required**. License Plate   |
| `vehicle_size`  | `string`           | **Required**. Vehicle Size    |


#### Edit Vehicle Record

```http
  POST /api/vehicles/${core_vehicle_id}
```

| Parameter       | Type               | Description                   |
| :-------------- | :----------------- | :-----------------------------|
| `api_key`       | `string`           | **Required**. Your API key    |
| `model`         | `string`           | **Required**. Vehicle Model   |
| `carrier_id`    | `string`           | **Required**. Core Carrier ID |
| `vehicle_id`    | `string`           | **Required**. Core Vehicle ID |
| `license_plate` | `string`           | **Required**. License Plate   |
| `vehicle_size`  | `string`           | **Required**. Vehicle Size    |


#### Get Single Vehicle

```http
  GET /api/vehicles/${core_vehicle_id}
```

| Parameter | Type      | Description                |
| :-------- | :-------- | :------------------------- |
| `api_key` | `string`  | **Required**. Your API key |


#### Get Vehicles

```http
  GET /api/vehicles
```

| Parameter | Type      | Description                |
| :-------- | :-------- | :------------------------- |
| `api_key` | `string`  | **Required**. Your API key |

## 
### Authors

- [@murungakibaara](https://www.gitlab.com/murungakibaara)

