import './App.css';
import {Component} from "react";
import PersonSelectionInputComponent from './components/PersonSelectionInputComponent.js'
import MealsTableComponent from "./components/MealsTableComponent";

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


const ROUTE_PERSONS = 'http://localhost:5000/api/persons/';

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


class App extends Component {
    constructor(props) {
        super(props);
        this.personSetter = this.personSetter.bind(this);
        this.actionChangeUser = this.actionChangeUser.bind(this)
        this.actionPostUser = this.actionPostUser.bind(this)
    }

    // state holds all the variables our site needs for functionality
    state = {
        // data will have the fetched body for the GET /persons/
        data: {},
        // person will have API URL for created person
        person: null,
        loggedIn: false
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
            person: userJson['@controls']['self']['href']
        });
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
        // TODO: REMOVE THIS
        // This is run when the page is opened or refreshed
        // Fetch the persons and store the body of the response
        // to the 'data'. The result is not yet used in any ways
        fetch('http://127.0.0.1:5000/api/persons/')
            .then(res => res.json())
            .then((data) => {
                this.setState({data: data})
            })
            .catch(console.log)
    }

// render() 'populates' our site with <div></div> components
// What's in here, appears on the screen.
    render() {
        let p
        if (this.state.person === null) {
            p = <AddPersonButton cb={this.actionPostUser}/>
        } else {
            p = <LoggedInUser id={this.state.person}/>
        }

        // let's import the static data from the included file, see the imports
        let dummyMeals = mealsJson

        return (
            <div>
            <div>
                <PersonSelectionInputComponent cb={this.handleChangeUserById}/>
                {p}
            </div>
            <div>
                <MealsTableComponent data={dummyMeals} />
            </div>
            </div>
        )
    }
}

export default App;
