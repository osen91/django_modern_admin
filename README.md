django_modern_admin
===================

DjangoModernAdmin is a materialize Django admin extension to for your web apps. 
With DjangoModernAdmin your dashboard will be more powerful and awesome.

You can download https://github.com/arifonursen/DjangoAdminSample.git and install requirements for test sample.

Quick start
-----------

![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/login.png)
![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/dashboard1.png)
![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/dashboard2.png)
![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/dashboard3.png)
![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/datefield.png)
![alt text](https://raw.githubusercontent.com/arifonursen/django_modern_admin/master/recent.png)

1. You can install with `pip install django_modern_admin`.Add “django_modern_admin” to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
    
        ‘django.contrib.auth’,
        ‘django_modern_admin’,
		‘django.contrib.admin’,
		‘... ‘
		
    ]
	
2. Requirements: Pillow, oauth2client

3. Run `python manage.py migrate` to create the django_modern_admin models.

4. You must define in settings.py 

	GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON = os.path.join(BASE_DIR, ‘xxx.json’)
	
	GOOGLE_ANALYTICS_ID = ‘123456789’

5. If you want to use charts you should set chart model and field in settings.py
	For Top Left Line Chart:
	
	TOP_LEFT_CHART = {
	
    	'title': 'Revenue',
    	'baseChartModel': 'Orders.Orders',
    	'baseChartLineField': 'orderTotal',
    	'baseChartDateField': 'orderDate',
    	'doughnutChartNameField': 'orderCategory',
    	'doughnutChartValueField': 'orderTotal',
    	'tableFieldsForDay': {'orderQty', 'productPrice', 'orderTotal'},
    	'tableFieldsForMonth': {'orderQty', 'orderTotal'}
    	
	}

	For Mini Bar Charts:
	
	MINI_BAR_CHART = {
	
    	'first': {
        	'icon': 'mdi-action-account-child', # optional
        	'chartModel': 'auth.User',
        	'chartModelDateField': 'date_joined',
        	'color': 'green',
    	},
    	'second': {
        	# 'icon': '', # optional
        	'chartModel': 'Orders.Orders',
        	'chartModelDateField': 'orderDate',
        	'color': 'deep-purple',
    	},
    	'third': {
        	'icon': 'mdi-action-announcement', # optional
        	'chartModel': 'auth.User',
        	'chartModelDateField': 'date_joined',
        	'color': 'blue-grey',
    	},
    	'fourth': {
        	# 'icon': '', # optional
        	'chartModel': 'Orders.Orders',
        	'chartModelDateField': 'orderDate',
        	'color': 'orange'
    	}
    	
	}
	
	For jVectorMap:

	VECTOR_MAP_JS_URL = '/static/js/plugins/jvectormap/jvector-turkey.js'

	For Left and Right Model List:
	
	MODEL_LIST = {
	
    	'left': {
        	'modelIcon': 'mdi-content-select-all',
        	'modelName': 'Products.Products',
        	'listFields': {'name', 'price', },
        	'filterField': 'price__lte', # optional
        	'filterValue': '400', # optional
        	'orderField': 'price',
    	},
    	'right': {
        	'modelName': 'Orders.Orders',
        	'listFields': ['product', 'orderQty'],
        	'orderField': 'orderDate'
    	}
    	
	}

	Footer Copyright:
	FOOTERCOPYRIGHT = ‘Django Modern Admin’ # optional
	
	Site Title:
	SITE_TITLE = ‘Django Modern Admin Administration’
	
	Site Header:
	SITE_HEADER = ‘Django Modern Admin Header’
	
	Index Title:
	INDEX_TITLE = ‘Django Modern Admin Index’

6. Visit http://127.0.0.1:8000/admin/ to see the magic.

