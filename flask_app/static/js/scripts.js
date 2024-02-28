price=0
function goto_product(id)
{
	window.location.href = "/item/view?id="+id;
}

function cart_delete(id)
{
	window.location.href = "/mycart?action=delete&id="+id;
}

function cart_clear()
{
	window.location.href = "/mycart?action=clear";
}

function quanity_change(me)
{
	const formatter = new Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',

	// These options are needed to round to whole numbers if that's what you want.
	//minimumFractionDigits: 0, // (this suffices for whole numbers, but will print 2500.10 as $2,500.1)
	//maximumFractionDigits: 0, // (causes 2500.99 to be printed as $2,501)
	});
	output=(formatter.format(me.value*price));
	console.log(output);
	item=document.querySelector("#js_total");
	if (item!=null)
	{
		item.innerText=output
	}
}

function loadit(me)
{
	me.value="1"
}