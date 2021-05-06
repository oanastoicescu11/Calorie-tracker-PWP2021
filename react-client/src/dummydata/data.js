let mealsString = '[{ \
            "id": "oatmeal", \
            "name": "Oatmeal", \
            "description": "Simple breakfast Oatmeal cooked in water", \
            "servings": 4,\
            "@controls": {\
                "collection": {\
                    "href": "/api/meals/"\
                },\
                "cameta:delete": {\
                    "method": "DELETE",\
                    "href": "/api/meals/oatmeal/"\
                },\
                "profile": {\
                    "href": "http://127.0.0.1"\
                },\
                "cameta:edit-meal": {\
                    "method": "PUT",\
                    "encoding": "json",\
                    "title": "Edits a Meal",\
                    "schema": {\
                        "type": "object",\
                        "required": [\
                            "id",\
                            "name",\
                            "servings"\
                        ],\
                        "properties": {\
                            "id": {\
                                "description": "usually meal name in small letters and white spaces replaced with dashes",\
                                "type": "string",\
                                "maxLength": 128,\
                                "pattern": "^[a-z,0-9]+(-[a-z,0-9]+)*$"\
                            },\
                            "name": {\
                                "description": "meal name",\
                                "type": "string",\
                                "maxLength": 128\
                            },\
                            "servings": {\
                                "description": "number of servings in this meal",\
                                "type": "integer"\
                            },\
                            "description": {\
                                "description": "Description of the meal",\
                                "type": "string",\
                                "maxLength": 8192\
                            }\
                        }\
                    },\
                    "href": "/api/meals/oatmeal/"\
                },\
                "self": {\
                    "href": "/api/meals/oatmeal/"\
                },\
                "cameta:meals-all": {\
                    "href": "/api/meals/"\
                }\
            },\
            "@namespaces": {\
                "cameta": {\
                    "name": "http://127.0.0.1"\
                }\
            }\
        }]'
let mealsJson = JSON.parse(mealsString)

export default mealsJson;