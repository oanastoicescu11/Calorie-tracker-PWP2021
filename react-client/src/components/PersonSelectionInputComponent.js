import {Component} from "react";

class PersonSelectionInputComponent extends Component {
// I found an example and copy-pasted this component here
    // and renamed it. https://reactjs.org/docs/forms.html
    // see `NameForm` on the site linked.
    constructor(props) {
        super(props);
        this.state = {value: ''};

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        // Send the given userId to callback and clear the input field
        this.props.cb(this.state.value)
        this.setState({value: ''})
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Login:
                    <input type="text" value={this.state.value} onChange={this.handleChange}/>
                </label>
                <input type="submit" value="Login"/>
            </form>
        );
    }
}

export default PersonSelectionInputComponent;