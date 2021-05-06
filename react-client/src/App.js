import './App.css';
import {Component, useState} from "react";
import PersonSelectionInputComponent from './components/PersonSelectionInputComponent.js'
import MealsTableComponent from "./components/MealsTableComponent";
import CreatePortionDialog from "./components/PortionDialog";
import MealDialog from "./components/MealDialog";
import mealsJson from "./dummydata/data";
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
const ROUTE_PORTIONS = 'http://localhost:5000/api/portions/';
const ROUTE_MEALPORTIONS = 'http://localhost:5000/api/mealportions/'
const SERVER_ROOT = 'http://localhost:5000'

class PostMealRecordButton extends Component {
    handleClick = () => {
        this.props.cb()
    }

    render() {
        return <button onClick={this.handleClick}>Post Mealrecord</button>
    }
}

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
class FetchMealsForPersonButton extends Component {
// AddPersonButton is a react component which
    //  1. Appears on the screen as a button
    //  2. When clicked prints a hello to the console
    //  3. And makes a POST request to create a new Person
    //  4. Saves returned 'Location' of the person to the application state
    handleClick = () => {
        console.log("FetchMealsForPerson clicked");
        this.props.cb();
    }

    render() {
        return <button onClick={this.handleClick}>Consumed Meals</button>
    }
}

class App extends Component {
    constructor(props) {
        super(props);
        this.personSetter = this.personSetter.bind(this);
        this.actionChangeUser = this.actionChangeUser.bind(this);
        this.actionPostUser = this.actionPostUser.bind(this);
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
        personMealRecordsJson: null
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
    async actionPostMealrecord() {
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
        let resp = await fetch(ROUTE_MEALS)
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
        let resp = await fetch(userUrl)
        if (!resp.ok) {
            console.log("404 user not found");
            alert('User not found with given ID');
            return;
        }
        let userJson = await resp.json()
        alert('Logging in user: ' + userUrl.split(ROUTE_PERSONS)[1]);
        this.actionChangeUser(userJson);
    }

    componentDidMount() {
        this.fetchMeals();
        this.fetchPortions();
    }

// render() 'populates' our site with <div></div> components
// What's in here, appears on the screen.
    render() {
        let personElement = null
        let fetchButton= <div></div>
        if (this.state.person === null) {
            personElement = <AddPersonButton cb={this.actionPostUser}/>
        } else {
            personElement = <LoggedInUser id={this.state.person.id}/>
            fetchButton = <FetchMealsForPersonButton cb={this.fetchMealsForPerson} />
        }

        // TODO: Remove the check for static data from here before release
        let mealsData = mealsJson
        if (this.state.mealsJson && this.state.mealsJson.items.length > 0)
            mealsData = this.state.mealsJson.items
        let portionsData = []
        if (this.state.portionsJson && this.state.portionsJson.items.length > 0)
            portionsData = this.state.portionsJson.items

        console.log(portionsData)
        return (
            <div>
                <div>
                    <PersonSelectionInputComponent cb={this.handleChangeUserById}/>
                    {personElement}
                </div>
                <div>
                    {fetchButton}
                </div>
                <div>
                    <MealsTableComponent data={mealsData}/>
                </div>
                <div>
                    <MealsTableComponent data={portionsData}/>
                </div>
                <div>
                    <CreatePortionDialog cb={this.createPortion}/>
                </div>
                <div>
                    <MealDialog cb={this.createMeal}/>
                </div>
            </div>
        )
    }
}

export default App;
