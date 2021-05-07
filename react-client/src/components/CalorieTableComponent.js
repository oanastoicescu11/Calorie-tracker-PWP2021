import {Component} from "react";

const RenderRow = (props) => {
    return props.keys.map((key, index) => {
        // Add index as part of the key, otherwise too many duplicate keys
        // in the same DOM
        return <td key={index + props.data[key]}>{props.data[key]}</td>
    })
}

class CalorieTableComponent extends Component {
// I found an example and copy-pasted this component here
    // and renamed it. https://reactjs.org/docs/forms.html
    // see `NameForm` on the site linked.
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.getKeysNotActions = this.getKeysNotActions.bind(this)
        this.getHeader = this.getHeader.bind(this)
        this.getRows = this.getRows.bind(this)
    }

    getKeysNotActions() {
        // Extract keys from the first item
        let allKeys = Object.keys(this.props.data[0]);
        // filter @control elements out
        return allKeys.filter(it => {
            return !it.startsWith("@")
        })
    }

    getHeader() {
        let keys = this.getKeysNotActions();
        return keys.map((key) => {
            return <th key={key}>{key.toUpperCase()}</th>
        })
    }

    getRows() {
        let items = this.props.data;
        let keys = this.getKeysNotActions();

        return items.map((row, index) => {
            return <tr key={index}><RenderRow key={index} data={row} keys={keys}/></tr>
        })
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        this.props.cb(this.state.value)
        event.preventDefault();
    }

    render() {
        let type = "items"
        if (this.props.type)
            type = this.props.type
        if (this.props.data.length > 0) {
            return (
                <div>
                <div>
                    <b>{type}</b>
                </div>
                <div>
                    <table>
                        <thead>
                        <tr>{this.getHeader()}</tr>
                        </thead>
                        <tbody>
                        {this.getRows()}
                        </tbody>
                    </table>
                </div>
                </div>
            );
        } else {
            return <div>No {type} found.</div>
        }
    }
}

export default CalorieTableComponent;