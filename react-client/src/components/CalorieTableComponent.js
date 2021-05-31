import {Component} from "react";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import MealDialogEdit from "./MealDialogEdit";
import MealDialog from "./MealDialog";

const RenderRow = (props) => {
    return props.keys.map((key, index) => {
        // Add index as part of the key, otherwise too many duplicate keys
        // in the same DOM
        return <TableCell key={index + props.data[key]}>{props.data[key]}</TableCell>
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
        this.edit = this.edit.bind(this)
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
        let headerKeys = keys.map((key) => {
            return <TableCell key={key}>{key.toUpperCase()}</TableCell>
        })
        return headerKeys
    }

    edit(index) {
        if (this.props.type !== "Meals")
            this.props.cb(this.props.data[index])
    }

    getRows() {
        let items = this.props.data;
        let keys = this.getKeysNotActions();

        let editFunction = () => {};
        // enable edit if type is Portions
        if (this.props.type === "Portions" || this.props.type === "Meals")
            editFunction = this.edit

        return items.map((row, index) => {
            if (this.props.type === "Meals") {
                row['EDIT'] = <div><MealDialogEdit meal={this.props.data[index]} cb={this.props.cb}/></div>
            }
            return <TableRow onClick={() => editFunction(index)} key={index}><RenderRow key={index} data={row} keys={keys}/></TableRow>
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
        if (this.props.type === "Portions")
            type = this.props.type + " (delete portion by click)"
        if (this.props.data.length > 0) {
            return (
                <div style={{backgroundColor: this.props.color}}>
                <div>
                    <b>{type}</b>
                </div>
                <div>
                    <Table>
                        <TableHead>
                        <TableRow>{this.getHeader()}</TableRow>
                        </TableHead>
                        <TableBody>
                        {this.getRows()}
                        </TableBody>
                    </Table>
                </div>
                </div>
            );
        } else {
            return <div>No {type} found.</div>
        }
    }
}

export default CalorieTableComponent;