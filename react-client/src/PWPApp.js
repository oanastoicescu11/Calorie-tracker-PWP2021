import './App.css';
import {Component} from "react";
import Grid from '@material-ui/core/Grid';
import PersonSelectionInputComponent from './components/PersonSelectionInputComponent.js'
import CalorieTableComponent from "./components/CalorieTableComponent";
import CreatePortionDialog from "./components/PortionDialog";
import MealDialog from "./components/MealDialog";
import MealRecordDialog from "./components/MealRecordDialog";

const LoggedInUser = (props) => {
    return (
        <div>
            <div>
                <div>Logged in user: {props.id}</div>
            </div>
            <div>
                <CalorieButton title="Logout" cb={props.cb}/>
            </div>
        </div>
    )
}

// TODO: These should come from the entrypoint request
const ROUTE_PERSONS = 'http://localhost:5000/api/persons/';
const ROUTE_MEALS = 'http://localhost:5000/api/meals/';
const ROUTE_MEALRECORDS = 'http://localhost:5000/api/mealrecords/';
const ROUTE_PORTIONS = 'http://localhost:5000/api/portions/';
const SERVER_ROOT = 'http://localhost:5000'
const API_ROOT = '/api/'

class CalorieButton extends Component {
    // 1. Appears on the screen as a button
    // 2. When clicked invokes the given callback
    // 3. Show Title as given title
    // 4. Log the click into Console
    handleClick = () => {
        console.log(this.props.title + " button clicked");
        this.props.cb();
    }

    render() {
        return <button onClick={this.handleClick}>{this.props.title}</button>
    }
}

class PWPApp extends Component {
    constructor(props) {
        super(props);
        this.actionChangeUser = this.actionChangeUser.bind(this);
        this.actionPostUser = this.actionPostUser.bind(this);
        this.actionPostMealrecord = this.actionPostMealrecord.bind(this);
        this.fetchMeals = this.fetchMeals.bind(this);
        this.fetchPortions = this.fetchPortions.bind(this);
        this.actionCreatePortion = this.actionCreatePortion.bind(this);
        this.actionPostMeal = this.actionPostMeal.bind(this);
        this.fetchMealsForPerson = this.fetchMealsForPerson.bind(this);
        this.handleLogout = this.handleLogout.bind(this);
        this.promptHelp = this.promptHelp.bind(this);
        this.deletePortion = this.deletePortion.bind(this);
        this.editMeal = this.editMeal.bind(this);
    }

    // state holds all the variables our site needs for functionality
    state = {
        // person will have API URL for created person
        person: null,
        loggedIn: false,
        mealsJson: null,
        portionsJson: null,
        personMealRecordsJson: null,
        controls: null, // @controls fetched from the API Entrypoint
        personControls: null // @controls specific to the Person
    }

    actionChangeUser = (userJson) => {
        console.log(userJson);
        // Simple Map (control -> href)
        let controls = new Map()
        Object.keys(userJson['@controls']).forEach((it) => {
            controls.set(it, userJson['@controls'][it]['href'])
        })
        this.setState({
            personControls: controls,
            loggedIn: true,
            person: userJson
        });
    }

    async fetchMealsForPerson() {
        // let uri = SERVER_ROOT + this.state.person['@controls']['cameta:mealrecords-by']['href']
        let uri = SERVER_ROOT + this.state.personControls.get('cameta:mealrecords-by')
        let resp = await fetch(uri)
            .catch((err) => {
                console.log(err)
            })
        if (!resp.ok) {
            console.log("UNABLE TO FETCH MEALS FOR PERSON!")
            return;
        }
        let data = await resp.json()
        this.setState({
            personMealRecordsJson: data
        })
        if (this.state.personMealRecordsJson.items.length === 0) {
            this.promptHelp()
        }
    }

    async actionPostMealrecord(name, amount, datetime) {
        console.log("POST: " + name + ", " + amount + ", " + datetime)

        let d = new Date(datetime).toISOString().replace('T', ' ').slice(0, -1);
        // TODO: @control...
        // let uri = SERVER_ROOT + this.state.person['@controls']['cameta:add-meal']['href']
        let postRequestOptions = {
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {
                    person_id: this.state.person.id,
                    meal_id: name,
                    amount: parseFloat(amount),
                    timestamp: d
                }
            ),
            method: 'POST'
        }
        // TODO: @controls...
        fetch(ROUTE_MEALRECORDS, postRequestOptions)
            .then((resp) => {
                if (resp.status === 409) {
                    console.log("409");
                    console.log(resp.headers);
                } else if (resp.status === 201) {
                    console.log(resp.headers);
                    // TODO: (future improvement) fetch and show a prompt of just created entity
                    // eslint-disable-next-line no-unused-vars
                    let location = resp.headers.get('Location');
                    this.fetchMealsForPerson()
                }
            })
    }

    async actionCreatePortion(name, calories) {
        let postRequestOptions = {
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {
                    id: name.toLowerCase(),
                    name: name,
                    calories: parseInt(calories)
                }),
            method: 'POST'
        }
        // TODO: @controls
        fetch(ROUTE_PORTIONS, postRequestOptions)
            .then((resp) => {
                if (resp.status === 409) {
                    console.log("409");
                    console.log(resp.headers);
                } else if (resp.status === 201) {
                    console.log(resp.headers);
                    // eslint-disable-next-line no-unused-vars
                    let location = resp.headers.get('Location');
                }
            }).then((_ => {
            this.fetchPortions()
        }))
    }

    createMealPortion(meal, portion, weightPerServing) {
        let postRequestOptions = {
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {
                    meal_id: meal.toLowerCase(),
                    portion_id: portion.toLowerCase(),
                    weight_per_serving: parseInt(weightPerServing)
                }),
            method: 'POST'
        }
        // TODO: @controls
        fetch(ROUTE_MEALS + meal + '/mealportions/', postRequestOptions)
            .then((resp) => {
                if (resp.status === 409) {
                    console.log("409");
                    console.log(resp.headers);
                } else if (resp.status === 201) {
                    console.log(resp.headers);
                    // eslint-disable-next-line no-unused-vars
                    let location = resp.headers.get('Location');
                }
            }).then((_ => {
            this.fetchMeals()
        }))
    }

    async actionPostMeal(name, servings, portions) {
        let postRequestOptions = {
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {
                    id: name.toLowerCase(),
                    name: name,
                    servings: parseInt(servings)
                }),
            method: 'POST'
        }
        // TODO: @controls...
        fetch(ROUTE_MEALS, postRequestOptions)
            .then((resp) => {
                if (resp.status === 409) {
                    console.log("409");
                    console.log(resp.headers);
                } else if (resp.status === 201) {
                    console.log(resp.headers);
                    // eslint-disable-next-line no-unused-vars
                    let location = resp.headers.get('Location');
                }
            }).then((_ => {
            portions.forEach((it) => {
                this.createMealPortion(name, it.portion, it.weightPerServing)
            })
        }))
    }

    async actionPostUser() {
        let t = new Date();
        let userId = "react-user-" + t.getHours() + '-' + t.getMinutes() + '-' + t.getSeconds();

        let postRequestOptions = {
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: userId}),
            method: 'POST'
        }
        fetch(ROUTE_PERSONS, postRequestOptions)
            .then((resp) => {
                if (resp.status === 409) {
                    console.log("409");
                    console.log(resp.headers);
                } else if (resp.status === 201) {
                    console.log(resp.headers);
                    let location = resp.headers.get('Location');
                    this.handleChangeUserByUrl(location)
                }
            })
    }

    async fetchMeals() {
        console.log(ROUTE_MEALS)
        console.log(SERVER_ROOT + this.state.controls.get('cameta:meals-all'))
        // let resp = await fetch(ROUTE_MEALS)
        let resp = await fetch(SERVER_ROOT + this.state.controls.get('cameta:meals-all'))
        if (!resp.ok) {
            console.log("UNABLE TO FETCH MEALS!")
            return;
        }
        let data = await resp.json()
        this.setState({
            mealsJson: data
        })
    }

    async fetchPortions() {
        let resp = await fetch(ROUTE_PORTIONS)
        if (!resp.ok) {
            console.log("UNABLE TO FETCH PORTIONS!")
            return;
        }
        console.log("GOT PORTIONS...")
        let data = await resp.json()
        console.log(data)
        this.setState({
            portionsJson: data
        })
    }

    handleLogout = () => {
        // empty userId logs out
        this.handleChangeUserById("")
    }
    handleChangeUserById = (userId) => {
        // Called when the Login button is clicked
        // Empty userId logs the user out
        if (userId.length > 0) {
            this.handleChangeUserByUrl(ROUTE_PERSONS + userId + '/');
        } else {
            alert("Logging out...");
            this.setState({
                loggedIn: false,
                person: null,
                personMealRecordsJson: null,
                personControls: null
            })
        }
    }

    async handleChangeUserByUrl(userUrl) {
        // Called only from the App Component
        // Fetch person by given Url and store in the State
        let resp = await fetch(userUrl)
        if (!resp.ok) {
            console.log("404 user not found");
            alert('User not found with given ID');
            return;
        }
        // Success
        let userJson = await resp.json()
        alert('Logging in user: ' + userUrl.split(ROUTE_PERSONS)[1]);
        this.actionChangeUser(userJson);
    }

    async initApp() {
        await this.fetchAPIControls()
        await this.fetchMeals();
        await this.fetchPortions();
    }

    async fetchAPIControls() {
        // Fetch root of the API for @controls
        // @controls are utilized further to fetch related data
        let resp = await fetch(SERVER_ROOT + API_ROOT)
        if (!resp.ok) {
            alert("Failed to fetch API controls: No API connection")
            return
        }

        // Success
        let data = await resp.json()

        // Simple Map (control -> href)
        let controls = new Map()
        Object.keys(data['@controls']).forEach((it) => {
            controls.set(it, data['@controls'][it]['href'])
        })
        this.setState({controls: controls})
    }

    promptHelp() {
        alert("HINT: Login as a '123' AND click 'Fetch Consumed Meals to view prepopulated data.")
    }

    componentDidMount() {
        // Page building starts here, when the view is opened in the browser
        this.initApp()
    }

    async editMeal(meal, name) {
        console.log("EDIT MEALLLL: " + meal.id + " " + name)
        console.log("EDIT MEALLLL: " + meal['@controls']['cameta:edit-meal']['href'])
        console.log("FUUUUUUU: " + meal['@controls']['self']['href'])

        fetch(SERVER_ROOT + meal['@controls']['self']['href'])
            .then(response =>
            response.json()
                .then(data => ({
                    data: data,
                    status: response.status
                })
            )
                .then(res => {
                console.log(res.status, res.data)
                    let putMeal = res.data
                    putMeal['name'] = name

                    let editUrl = putMeal['@controls']['cameta:edit-meal']['href']
                    for (let propName in putMeal) {
                        if (propName.startsWith('@'))
                            delete putMeal[propName];
                    }
                    if (putMeal['description'] === null)
                        putMeal['description'] = ''
                    let putRequestOptions = {
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(putMeal),
                        method: 'PUT'
                    }
                    fetch(SERVER_ROOT + editUrl, putRequestOptions)
                        .then((resp: Response) => {
                            if (!resp.ok)
                                alert("Unable to rename the Meal!")
                        }).then(_ => {
                            this.fetchMeals();
                    })
            }))

    }

    async deletePortion(portion) {
        let resp = await fetch(SERVER_ROOT + portion['@controls']['cameta:delete']['href'], {method: 'DELETE'})
        if (!resp.ok)
            alert("Unable to delete the Portion, maybe you have defined meals with the Portion included?")
        else
            await this.fetchPortions()
    }

// render() 'populates' our site with <div></div> components
// What is returned from here, appears on the screen.
    render() {
        let personElement // either show Create Person and Login -button or Logged in Person Id
        let fetchMealRecordsForPersonButton = <div></div>
        let createMealRecordButton = <div></div>
        if (this.state.person === null) {
            // Not logged in, show option to create a new Person
            personElement = <CalorieButton title="Generate a new User" cb={this.actionPostUser}/>
        } else {
            // Logged in, show all Person related fields
            personElement = <LoggedInUser id={this.state.person.id} cb={this.handleLogout}/>
            fetchMealRecordsForPersonButton =
                <CalorieButton title="Fetch Consumed Meals" cb={this.fetchMealsForPerson}/>
            createMealRecordButton = <MealRecordDialog cb={this.actionPostMealrecord}/>
        }

        // All tables are either empty or have real data if already fetched
        let mealsData = []
        if (this.state.mealsJson && this.state.mealsJson.items.length > 0)
            mealsData = this.state.mealsJson.items
        let portionsData = []
        if (this.state.portionsJson && this.state.portionsJson.items.length > 0)
            portionsData = this.state.portionsJson.items
        let mealRecordsData = []
        if (this.state.personMealRecordsJson && this.state.personMealRecordsJson.items.length > 0)
            mealRecordsData = this.state.personMealRecordsJson.items

        // Here we place the Elements on the screen
        return (
            <div>
                <Grid container spacing={3}>
                    {/*Start of the grid*/}
                    <Grid item xs={12}>
                        {/*Login Grid*/}
                        <div style={{backgroundColor: "red"}}>
                            <PersonSelectionInputComponent cb={this.handleChangeUserById}/>
                            {personElement}
                        </div>
                    </Grid>
                    <Grid item xs={9}>
                        {/* Meal Records Grid*/}
                        <div style={{backgroundColor: "lightblue"}}>
                            {fetchMealRecordsForPersonButton}
                        </div>
                        <div>
                            <CalorieTableComponent type="Consumed Meals" data={mealRecordsData} color={"lightblue"}/>
                        </div>
                        <div>
                            {createMealRecordButton}
                        </div>
                    </Grid>
                    <Grid item xs={9}>
                        {/*Meals Grid*/}
                        <div>
                            <CalorieTableComponent type="Meals" data={mealsData} color={"orange"} cb={this.editMeal}/>
                        </div>
                        <div>
                            <MealDialog cb={this.actionPostMeal}/>
                        </div>
                    </Grid>
                    <Grid item xs={9}>
                        {/*Portions Grid*/}
                        <div>
                            <CalorieTableComponent type="Portions" data={portionsData} color={"lightgreen"}
                                                   cb={this.deletePortion}/>
                        </div>
                        <div>
                            <CreatePortionDialog cb={this.actionCreatePortion}/>
                        </div>
                    </Grid>
                </Grid>
                <CalorieButton title="Help!" cb={this.promptHelp}/>
            </div>
        )
    }
}

export default PWPApp;
