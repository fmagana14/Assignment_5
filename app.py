from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
# from pymongo import MongoClient
# The Following code ia my own 
uri = "mongodb+srv://FMuser:KoolWordz@cluster0.ykezvyd.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient('localhost', 27017)
db = client.flask_db
plants = db.plants

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = plants.find()  # Retrieve all plants from the MongoDB collection
    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant = {
            'name': request.form['name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo_url'],
            'date_planted': request.form['date_planted']
        }
        # Insert the new plant into the database
        result = plants.insert_one(new_plant)
        # Redirect to the detail page of the newly created plant
        return redirect(url_for('detail', plant_id=result.inserted_id))
    else:
        return render_template('create.html')
    
@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    plant_to_show = plants.find_one({'_id': ObjectId(plant_id)})
    harvests = db.harvests.find({'plant_id': plant_id})
    context = {
        'plant': plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    new_harvest = {
        'quantity': request.form['quantity'],
        'date': request.form['date'],
        'plant_id': plant_id
    }
    db.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    if request.method == 'POST':
        # Update the plant with the given id
        plants.update_one(
            {'_id': ObjectId(plant_id)},
            {'$set': {
                'name': request.form['name'],
                'variety': request.form['variety'],
                'photo_url': request.form['photo_url'],
                'date_planted': request.form['date_planted']
            }}
        )
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = plants.find_one({'_id': ObjectId(plant_id)})
        context = {
            'plant': plant_to_show
        }
        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    # Delete the plant with the given id
    plants.delete_one({'_id': ObjectId(plant_id)})
    # Delete all harvests associated with the plant
    db.harvests.delete_many({'plant_id': plant_id})
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

