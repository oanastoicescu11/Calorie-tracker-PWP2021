import './App.css';
import {Component} from "react";
import Grid from '@material-ui/core/Grid';
import PersonSelectionInputComponent from './components/PersonSelectionInputComponent.js'
import CalorieTableComponent from "./components/CalorieTableComponent";
import CreatePortionDialog from "./components/PortionDialog";
import MealDialog from "./components/MealDialog";
import MealRecordDialog from "./components/MealRecordDialog";
// Please, remove all the unused code
// I'm just checking this code in to get things
// moving forward.

const SimpleItem = (props) => {
    const {id} = props;
    return (
        <div>Element ID: {id}</div>
    )
}

const LoggedInUser = (props) => {
    const {id} = props;
    return (
        <div>Logged in user: {id}</div>
    )
}

class SimpleComponent extends Component {
    render() {
        const {id} = this.props;
        return <div>component hello {id}</div>
    }
}

const SimplePersonGreeter = (props) => {
    // const {name, id} = this.props
    return <div>SimpleStateComponent: Hello {props.name}! your id is <b>{props.id}</b></div>
}

class SimpleStateComponent extends Component {
    state = {
        id: "123",
        name: "John Doe"
    }

    render() {
        const {name} = this.state;
        const {id} = this.state;
        return <div>SimpleStateComponent: Hello {name}! your id is <b>{id}</b></div>
    }
}

// TODO: These should come from the entrypoint request
const ROUTE_PERSONS = 'http://localhost:5000/api/persons/';
const ROUTE_MEALS = 'http://localhost:5000/api/meals/';
const ROUTE_MEALRECORDS = 'http://localhost:5000/api/mealrecords/';
const ROUTE_PORTIONS = 'http://localhost:5000/api/portions/';
const SERVER_ROOT = 'http://localhost:5000'
const API_ROOT = '/api/'
class AddPersonButton extends Component {
// AddPersonButton is a react component which
    //  1. Appears on the screen as a button
    //  2. When clicked prints a hello to the console
    //  3. And makes a POST request to create a new Person
    //  4. Saves returned 'Location' of the person to the application state
    handleCreatePersonButtonClick = () => {
        console.log("AddPersonButton clicked");
        this.props.cb();
    }

    render() {
        return <button onClick={this.handleCreatePersonButtonClick}>Add Person</button>
    }
}

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

class App extends Component {
    constructor(props) {
        super(props);
        this.personSetter = this.personSetter.bind(this);
        this.actionChangeUser = this.actionChangeUser.bind(this);
        this.actionPostUser = this.actionPostUser.bind(this);
        this.actionPostMealrecord = this.actionPostMealrecord.bind(this);
        this.fetchMeals = this.fetchMeals.bind(this);
        this.fetchPortions = this.fetchPortions.bind(this);
        this.createPortion = this.createPortion.bind(this);
        this.createMeal = this.createMeal.bind(this);
        this.fetchMealsForPerson = this.fetchMealsForPerson.bind(this);
    }

    // state holds all the variables our site needs for functionality
    state = {
        // data will have the fetched body for the GET /persons/
        data: {},
        // person will have API URL for created person
        person: null,
        loggedIn: false,
        mealsJson: null,
        portionsJson: null,
        personMealRecordsJson: null,
        controls: null
    }
    personSetter = (person) => {
        // THIS is called when the Add Person button is clicked
        console.log("SET STATE: " + person)

        this.setState({
            // Let's store the URL to the person
            person: person
        })
    }

    actionChangeUser = (userJson) => {
        console.log(userJson);
        this.setState({
            loggedIn: true,
            person: userJson
        });
    }

    async fetchMealsForPerson() {
        let uri = SERVER_ROOT + this.state.person['@controls']['cameta:mealrecords-by']['href']
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
                    // TODO: (future imporovement) fetch and show a prompt of just created entity
                    // eslint-disable-next-line no-unused-vars
                    let location = resp.headers.get('Location');
                    this.fetchMealsForPerson()
                }
            })
    }

    async createPortion(name, calories) {
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
                    let location = resp.headers.get('Location');
                    // this.handleChangeUserByUrl(location
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
                    let location = resp.headers.get('Location');
                }
            }).then((_ => {
            this.fetchMeals()
        }))
    }

    async createMeal(name, servings, portions) {
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

    handleChangeUserById = (userId) => {
        // Called when the Login button is clicked
        // Empty userId logs the user out
        if (userId.length > 0) {
            this.handleChangeUserByUrl(ROUTE_PERSONS + userId + '/');
        } else {
            alert("Logging out...");
            this.setState({
                loggedIn: false,
                person: null
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
    componentDidMount() {
        // Page building starts here, when the view is opened in the browser
        this.initApp()
    }

// render() 'populates' our site with <div></div> components
// What is returned from here, appears on the screen.
    render() {
        let personElement // either show Create Person and Login -button or Logged in Person Id
        let fetchMealRecordsForPersonButton = <div></div>
        let createMealRecordButton = <div></div>
        if (this.state.person === null) {
            // Not logged in, show option to create a new Person
            personElement = <AddPersonButton cb={this.actionPostUser}/>
        } else {
            // Logged in, show all Person related fields
            personElement = <LoggedInUser id={this.state.person.id}/>
            fetchMealRecordsForPersonButton = <CalorieButton title="Fetch Consumed Meals" cb={this.fetchMealsForPerson}/>
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
                        <div style={{backgroundColor: "blue"}}>
                            {fetchMealRecordsForPersonButton}
                        </div>
                        <div style={{backgroundColor: "blue"}}>
                            <CalorieTableComponent type="Consumed Meals" data={mealRecordsData}/>
                        </div>
                        <div style={{backgroundColor: "blue"}}>
                            {createMealRecordButton}
                        </div>
                    </Grid>
                    <Grid item xs={9}>
                        {/*Meals Grid*/}
                        <div style={{backgroundColor: "orange"}}>
                            <CalorieTableComponent type="Meals" data={mealsData}/>
                        </div>
                        <div style={{backgroundColor: "orange"}}>
                            <MealDialog cb={this.createMeal}/>
                        </div>
                    </Grid>
                    <Grid item xs={9}>
                        {/*Portions Grid*/}
                        <div style={{backgroundColor: "lightgreen"}}>
                            <CalorieTableComponent type="Portions" data={portionsData}/>
                        </div>
                        <div style={{backgroundColor: "lightgreen"}}>
                            <CreatePortionDialog cb={this.createPortion}/>
                        </div>
                    </Grid>
                </Grid>
            </div>
        )
    }
}

export default App;
